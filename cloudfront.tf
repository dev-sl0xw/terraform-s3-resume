# CloudFront 배포 리소스
# 요구사항 2.1, 2.4, 7.2 구현

# Origin Access Control (OAC) 생성
# 요구사항 2.4, 7.2: S3 버킷에 안전하게 접근하기 위한 OAC 구성
resource "aws_cloudfront_origin_access_control" "resume_oac" {
  name                              = "resume-oac-${var.environment}"
  description                       = "OAC for Resume S3 Bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "resume_distribution" {
  enabled = true
  comment = "Resume hosting distribution"
  
  origin {
    domain_name              = aws_s3_bucket.resume_bucket.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.resume_bucket.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.resume_oac.id
  }
  
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.resume_bucket.id}"
    viewer_protocol_policy = "allow-all"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
