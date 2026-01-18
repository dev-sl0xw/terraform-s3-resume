# S3 Outputs
output "s3_bucket_name" {
  description = "생성된 S3 버킷 이름"
  value       = aws_s3_bucket.resume_bucket.id
}

output "s3_bucket_arn" {
  description = "S3 버킷 ARN"
  value       = aws_s3_bucket.resume_bucket.arn
}

# CloudFront Outputs
output "cloudfront_distribution_id" {
  description = "CloudFront 배포 ID"
  value       = aws_cloudfront_distribution.resume_distribution.id
}

output "cloudfront_distribution_arn" {
  description = "CloudFront 배포 ARN"
  value       = aws_cloudfront_distribution.resume_distribution.arn
}

output "cloudfront_domain_name" {
  description = "CloudFront 배포 도메인 이름"
  value       = aws_cloudfront_distribution.resume_distribution.domain_name
}

output "cloudfront_oac_id" {
  description = "CloudFront Origin Access Control ID"
  value       = aws_cloudfront_origin_access_control.resume_oac.id
}

# output "custom_domain_url" {
#   description = "커스텀 도메인을 통한 이력서 URL"
#   value       = "https://${var.custom_domain}/${var.resume_filename}"
# }

# ACM Outputs (uncomment after ACM is deployed)
# output "acm_certificate_arn" {
#   description = "ACM 인증서 ARN"
#   value       = aws_acm_certificate.resume_cert.arn
# }

# Route53 Outputs (uncomment after Route53 is deployed)
# output "route53_record_name" {
#   description = "Route53 레코드 이름"
#   value       = aws_route53_record.resume.name
# }

# Helper Commands (uncomment after full deployment)
# output "upload_command" {
#   description = "이력서를 S3에 업로드하는 AWS CLI 명령"
#   value       = "aws s3 cp ${var.resume_filename} s3://${aws_s3_bucket.resume_bucket.id}/${var.resume_filename} --content-type application/pdf"
# }

# output "invalidate_cache_command" {
#   description = "CloudFront 캐시를 무효화하는 AWS CLI 명령"
#   value       = "aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.resume_distribution.id} --paths '/*'"
# }
