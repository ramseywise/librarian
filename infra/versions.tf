terraform {
  # 1.10 is the first release of both Terraform and OpenTofu with S3-native state locking
  # (`use_lockfile`), so no DynamoDB table is needed.
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # Partial configuration: the bucket and region are not written here. Pass them at init:
  #   terraform init -backend-config="bucket=<state bucket>" -backend-config="region=<region>" \
  #     -backend-config="key=librarian/prod.tfstate"
  # (one key per environment). See README.md.
  backend "s3" {
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "librarian"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
