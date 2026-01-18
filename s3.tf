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
