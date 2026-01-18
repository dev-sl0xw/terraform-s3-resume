# Terraform Infrastructure Tests

이 디렉토리는 Terraform으로 프로비저닝된 AWS 인프라를 검증하는 테스트를 포함합니다.

## 사전 요구사항

1. Python 3.8 이상
2. AWS 자격 증명 구성 (AWS CLI 또는 환경 변수)
3. Terraform으로 인프라가 이미 배포되어 있어야 함

## 설치

테스트 의존성 설치:

```bash
pip install -r tests/requirements.txt
```

또는 가상 환경 사용:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r tests/requirements.txt
```

## 테스트 실행

### 모든 테스트 실행

```bash
pytest tests/
```

### 특정 테스트 파일 실행

```bash
pytest tests/test_s3_bucket_config.py
```

### 특정 테스트 함수 실행

```bash
pytest tests/test_s3_bucket_config.py::test_s3_bucket_exists
```

### 상세 출력으로 실행

```bash
pytest tests/ -v
```

### 마커로 필터링

```bash
# 통합 테스트만 실행
pytest tests/ -m integration

# 속성 기반 테스트만 실행
pytest tests/ -m property
```

## 테스트 구조

### test_s3_bucket_config.py

S3 버킷 구성 검증 테스트 (Task 2.2):
- `test_s3_bucket_exists`: S3 버킷 존재 확인
- `test_s3_versioning_enabled`: 버전 관리 활성화 확인
- `test_s3_public_access_blocked`: 공개 접근 차단 확인
- `test_s3_bucket_tags`: 버킷 태그 확인

**요구사항**: 1.1, 1.3, 1.5

## AWS 자격 증명

테스트는 AWS 자격 증명이 필요합니다. 다음 방법 중 하나를 사용하세요:

1. **AWS CLI 프로파일**:
   ```bash
   export AWS_PROFILE=your-profile
   pytest tests/
   ```

2. **환경 변수**:
   ```bash
   export AWS_ACCESS_KEY_ID=your-access-key
   export AWS_SECRET_ACCESS_KEY=your-secret-key
   export AWS_DEFAULT_REGION=us-east-1
   pytest tests/
   ```

3. **IAM 역할** (EC2/ECS에서 실행 시):
   자동으로 인스턴스 메타데이터에서 자격 증명을 가져옵니다.

## 문제 해결

### "Terraform outputs not available" 오류

인프라가 배포되지 않았거나 terraform 명령을 찾을 수 없습니다:

```bash
cd terraform-s3-resume
terraform init
terraform apply
```

### AWS 권한 오류

테스트를 실행하는 IAM 사용자/역할에 다음 권한이 필요합니다:
- `s3:GetBucketVersioning`
- `s3:GetPublicAccessBlock`
- `s3:GetBucketTagging`
- `s3:HeadBucket`

### boto3 ImportError

의존성을 설치하세요:

```bash
pip install -r tests/requirements.txt
```

## CI/CD 통합

GitHub Actions 예제:

```yaml
- name: Run Infrastructure Tests
  run: |
    pip install -r tests/requirements.txt
    pytest tests/ -v
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    AWS_DEFAULT_REGION: us-east-1
```
