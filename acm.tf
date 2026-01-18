# ACM 인증서 리소스
# Task 4에서 구현 예정

resource "aws_acm_certificate" "resume_cert" {
  provider          = aws.us_east_1
  domain_name       = var.custom_domain
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = {
    Name        = "Resume Certificate"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
