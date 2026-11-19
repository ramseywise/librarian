variable "region" {
  description = "AWS region for the host."
  type        = string
  default     = "eu-west-1"
}

variable "environment" {
  description = "Name of this stack, used in resource names and tags: prod or staging."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,19}$", var.environment))
    error_message = "environment must be 2-20 characters: lower-case letters, digits and hyphens, starting with a letter."
  }
}

variable "architecture" {
  description = "CPU architecture of the instance: x86_64 or arm64. CI builds linux/amd64 only (see README.md), so arm64 needs a multi-platform image build first."
  type        = string
  default     = "x86_64"

  validation {
    condition     = contains(["x86_64", "arm64"], var.architecture)
    error_message = "architecture must be x86_64 or arm64."
  }
}

variable "instance_type" {
  description = "EC2 instance type. Must match var.architecture (t3/m7i are x86_64; t4g/m7g are arm64). The default is a justified guess, not a measurement: see README.md."
  type        = string
  default     = "t3.large"
}

variable "volume_size_gb" {
  description = "Size of the encrypted gp3 root volume in GiB. It holds the OS, Docker images, and the Postgres, search-index, Prometheus and Grafana volumes."
  type        = number
  default     = 40

  validation {
    condition     = var.volume_size_gb >= 30 && var.volume_size_gb <= 16384
    error_message = "volume_size_gb must be between 30 and 16384."
  }
}

variable "domain" {
  description = "Public host name (LIBRARIAN_DOMAIN), for example librarian.example.org. Used only for the DNS record and the outputs; null skips both."
  type        = string
  default     = null
}

variable "route53_zone_id" {
  description = "Route 53 hosted zone id that contains var.domain. When null, no record is created and the address to set by hand is an output."
  type        = string
  default     = null
}

variable "dns_ttl" {
  description = "TTL in seconds of the Route 53 A record."
  type        = number
  default     = 300
}
