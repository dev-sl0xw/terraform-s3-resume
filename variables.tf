variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "환경 이름 (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "bucket_name" {
  description = "S3 버킷 이름 (전역적으로 고유해야 함)"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.bucket_name))
    error_message = "버킷 이름은 소문자, 숫자, 하이픈만 포함해야 하며 하이픈으로 시작하거나 끝날 수 없습니다."
  }
}

variable "resume_filename" {
  description = "S3에 업로드할 이력서 PDF 파일 이름"
  type        = string
  default     = "resume.pdf"
  validation {
    condition     = can(regex("\\.pdf$", var.resume_filename))
    error_message = "이력서 파일 이름은 .pdf로 끝나야 합니다."
  }
}

variable "custom_domain" {
  description = "이력서를 위한 커스텀 도메인 (예: resume.yourdomain.com)"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]*[a-z0-9]$", var.custom_domain))
    error_message = "유효한 도메인 이름을 제공해야 합니다."
  }
}

variable "root_domain" {
  description = "Route53 호스팅 영역의 루트 도메인 (예: yourdomain.com)"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]*[a-z0-9]$", var.root_domain))
    error_message = "유효한 도메인 이름을 제공해야 합니다."
  }
}

variable "tags" {
  description = "모든 리소스에 적용할 추가 태그"
  type        = map(string)
  default     = {}
}
