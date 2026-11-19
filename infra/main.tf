# One librarian host: EC2 instance, encrypted gp3 volume, security group (80 and 443 only),
# Elastic IP, and an IAM role so a shell comes from SSM Session Manager instead of SSH.
# Nothing here deploys the app or holds a secret; see user_data.sh and README.md.

locals {
  name = "librarian-${var.environment}"
}

# The default VPC keeps this configuration to one host. If the account has no default VPC,
# `plan` fails on these data sources: create one or replace them with your own VPC and subnet.
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

# Ubuntu 24.04 LTS from Canonical's public SSM parameter. The AMI is looked up at plan time,
# so a newer image makes the instance be replaced: see ignore_changes below.
data "aws_ssm_parameter" "ubuntu" {
  name = "/aws/service/canonical/ubuntu/server/24.04/stable/current/${var.architecture == "arm64" ? "arm64" : "amd64"}/hvm/ebs-gp3/ami-id"
}

resource "aws_security_group" "host" {
  name        = local.name
  description = "librarian ${var.environment}: HTTP and HTTPS in, nothing else (no SSH)"
  vpc_id      = data.aws_vpc.default.id
}

# 80 stays open for Caddy's certificate challenge and the redirect to HTTPS.
resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.host.id
  description       = "HTTP"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.host.id
  description       = "HTTPS"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}

# Outbound is open: image pulls, apt, Let's Encrypt, the Anthropic API, S3, and the SSM endpoints.
resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.host.id
  description       = "All outbound"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "host" {
  name               = "${local.name}-host"
  description        = "SSM Session Manager access for the ${local.name} host"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

# The AWS-managed policy for the SSM agent. It grants no access to S3 or anything else.
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.host.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "host" {
  name = "${local.name}-host"
  role = aws_iam_role.host.name
}

resource "aws_instance" "host" {
  ami                    = nonsensitive(data.aws_ssm_parameter.ubuntu.value)
  instance_type          = var.instance_type
  subnet_id              = sort(data.aws_subnets.default.ids)[0]
  vpc_security_group_ids = [aws_security_group.host.id]
  iam_instance_profile   = aws_iam_instance_profile.host.name

  # Plain script, no secret, no deploy. A change replaces the instance, so keep it small.
  user_data                   = file("${path.module}/user_data.sh")
  user_data_replace_on_change = true

  # IMDSv2 only. A hop limit of 1 keeps containers from reaching the metadata service.
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.volume_size_gb
    encrypted             = true
    delete_on_termination = true
  }

  tags = {
    Name = local.name
  }

  lifecycle {
    # A new Ubuntu image must not replace a host that holds the database volume.
    ignore_changes = [ami]

    precondition {
      condition     = (var.architecture == "arm64") == can(regex("^[a-z]+[0-9]+g[a-z]*\\.", var.instance_type))
      error_message = "instance_type ${var.instance_type} does not match architecture ${var.architecture} (arm64 types have a g after the generation, such as t4g or m7g)."
    }
  }
}

resource "aws_eip" "host" {
  domain   = "vpc"
  instance = aws_instance.host.id

  tags = {
    Name = local.name
  }
}

resource "aws_route53_record" "host" {
  count = var.route53_zone_id != null && var.domain != null ? 1 : 0

  zone_id = var.route53_zone_id
  name    = var.domain
  type    = "A"
  ttl     = var.dns_ttl
  records = [aws_eip.host.public_ip]
}
