output "instance_id" {
  description = "EC2 instance id: aws ssm start-session --target <this>."
  value       = aws_instance.host.id
}

output "public_ip" {
  description = "Elastic IP of the host."
  value       = aws_eip.host.public_ip
}

output "dns_record" {
  description = "What to do about DNS."
  value = (
    length(aws_route53_record.host) > 0
    ? "Route 53 record created: ${var.domain} A ${aws_eip.host.public_ip}"
    : "No Route 53 record. Create this one by hand: ${coalesce(var.domain, "<LIBRARIAN_DOMAIN>")} A ${aws_eip.host.public_ip}"
  )
}

output "ssm_command" {
  description = "Command that opens a shell on the host (needs the AWS CLI and the Session Manager plugin on your machine)."
  value       = "aws ssm start-session --region ${var.region} --target ${aws_instance.host.id}"
}
