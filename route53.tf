# Route53 DNS 레코드 리소스
# Task 4, 7에서 구현 예정
# 참고: Route53 호스팅 영역이 존재할 때 아래 주석을 해제하세요

# data "aws_route53_zone" "main" {
#   name         = var.root_domain
#   private_zone = false
# }

# resource "aws_route53_record" "resume" {
#   zone_id = data.aws_route53_zone.main.zone_id
#   name    = var.custom_domain
#   type    = "A"
#   
#   alias {
#     name                   = aws_cloudfront_distribution.resume_distribution.domain_name
#     zone_id                = aws_cloudfront_distribution.resume_distribution.hosted_zone_id
#     evaluate_target_health = false
#   }
# }
