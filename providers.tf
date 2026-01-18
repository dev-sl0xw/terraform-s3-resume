terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # 선택사항: 원격 상태 저장소 (S3 + DynamoDB)
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "resume-hosting/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = merge(
      {
        Project   = "Resume Hosting"
        ManagedBy = "Terraform"
      },
      var.tags
    )
  }
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
  
  default_tags {
    tags = merge(
      {
        Project   = "Resume Hosting"
        ManagedBy = "Terraform"
      },
      var.tags
    )
  }
}
