# S3 버킷 리소스
# 요구사항 1.1, 1.3, 1.5 구현

resource "aws_s3_bucket" "resume_bucket" {
  bucket = var.bucket_name
  
  tags = {
    Name        = "Resume Hosting Bucket"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# S3 버킷 버전 관리 활성화
# 요구사항 1.5: 이력서 업데이트 추적 및 롤백 가능
resource "aws_s3_bucket_versioning" "resume_versioning" {
  bucket = aws_s3_bucket.resume_bucket.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 버킷 공개 접근 차단
# 요구사항 1.3: 비공개 접근으로 구성 (공개적으로 접근 불가)
resource "aws_s3_bucket_public_access_block" "resume_public_access_block" {
  bucket = aws_s3_bucket.resume_bucket.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 버킷 정책
# 요구사항 2.4, 7.2: CloudFront OAC만 S3 버킷에 접근 허용
resource "aws_s3_bucket_policy" "resume_bucket_policy" {
  bucket = aws_s3_bucket.resume_bucket.id
  
  # public_access_block이 먼저 적용되어야 함
  depends_on = [aws_s3_bucket_public_access_block.resume_public_access_block]
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontServicePrincipal"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.resume_bucket.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.resume_distribution.arn
          }
        }
      }
    ]
  })
}
