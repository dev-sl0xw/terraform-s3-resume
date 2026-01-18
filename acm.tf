# ACM 인증서 리소스
# 요구사항 3.2, 3.5: 커스텀 도메인을 위한 SSL/TLS 인증서 프로비저닝
# 중요: CloudFront용 ACM 인증서는 반드시 us-east-1 리전에서 생성해야 합니다
#
# 참고: Route53 호스팅 영역이 현재 AWS 계정에 존재해야 자동 DNS 검증이 가능합니다.
# 지인의 계정에 호스팅 영역이 있는 경우:
# 1. ACM 인증서 생성 후 domain_validation_options 출력값 확인
# 2. 지인에게 CNAME 레코드 생성 요청
# 3. 검증 완료 후 CloudFront에 인증서 연결

# ACM 인증서 생성
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

# ACM 인증서 검증에 필요한 DNS 레코드 정보 출력
output "acm_validation_records" {
  description = "ACM 인증서 DNS 검증에 필요한 CNAME 레코드 (지인에게 전달)"
  value = {
    for dvo in aws_acm_certificate.resume_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      value  = dvo.resource_record_value
    }
  }
}

# ACM 인증서 ARN 출력
output "acm_certificate_arn" {
  description = "ACM 인증서 ARN"
  value       = aws_acm_certificate.resume_cert.arn
}
