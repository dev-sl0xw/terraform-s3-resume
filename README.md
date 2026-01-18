# Resume Hosting Infrastructure

Terraform을 사용하여 AWS에서 PDF 이력서를 호스팅하는 인프라입니다.

## 아키텍처

- **S3**: PDF 이력서 파일 저장 (비공개)
- **CloudFront**: CDN을 통한 전 세계적 콘텐츠 전송
- **Route53**: 커스텀 도메인 DNS 관리
- **ACM**: 무료 SSL/TLS 인증서

## 프로젝트 구조

```
terraform-s3-resume/
├── providers.tf              # AWS 프로바이더 구성
├── variables.tf              # 입력 변수 정의
├── outputs.tf                # 출력 값 정의
├── s3.tf                     # S3 버킷 리소스
├── cloudfront.tf             # CloudFront 배포 리소스
├── acm.tf                    # ACM 인증서 리소스
├── route53.tf                # Route53 DNS 레코드
├── terraform.tfvars.example  # 변수 예제 파일
├── .gitignore                # Git 무시 파일
└── README.md                 # 이 파일
```

## 사전 요구사항

1. **AWS 계정**: 활성화된 AWS 계정
2. **Terraform**: 버전 1.0 이상 설치
3. **AWS CLI**: 구성된 AWS 자격 증명
4. **Route53 호스팅 영역**: 도메인에 대한 호스팅 영역 존재

## 초기 설정

1. **변수 파일 생성**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **terraform.tfvars 편집**:
   - `bucket_name`: 전역적으로 고유한 S3 버킷 이름
   - `custom_domain`: 이력서 접근용 도메인 (예: resume.yourdomain.com)
   - `root_domain`: Route53 호스팅 영역의 루트 도메인

3. **Terraform 초기화**:
   ```bash
   terraform init
   ```

4. **구성 검증**:
   ```bash
   terraform validate
   ```

5. **계획 검토**:
   ```bash
   terraform plan
   ```

## 배포

```bash
terraform apply
```

## 이력서 업로드

배포 완료 후, 출력된 명령을 사용하여 이력서를 업로드합니다:

```bash
aws s3 cp resume.pdf s3://your-bucket-name/resume.pdf --content-type application/pdf
```

## 캐시 무효화

이력서 업데이트 후 CloudFront 캐시를 무효화합니다:

```bash
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths '/*'
```

## 비용 최적화

이 인프라는 AWS 프리 티어 범위 내에서 작동하도록 최적화되었습니다:

- **S3**: 5GB 스토리지, 20,000 GET 요청/월
- **CloudFront**: 1TB 데이터 전송, 10,000,000 요청/월
- **Route53**: $0.50/월 (호스팅 영역)
- **ACM**: 무료

예상 월간 비용: **$0.50 ~ $1.50**

## 정리

모든 리소스를 삭제하려면:

```bash
terraform destroy
```

## 구현 상태

- [x] Task 1: Terraform 프로젝트 구조 및 기본 구성 설정
- [ ] Task 2: S3 버킷 리소스 구현
- [ ] Task 3: CloudFront Origin Access Control 및 S3 버킷 정책 구현
- [ ] Task 4: ACM SSL 인증서 프로비저닝
- [ ] Task 5: CloudFront 배포 구성
- [ ] Task 7: Route53 DNS 레코드 구성
- [ ] Task 8: Terraform 멱등성 및 구성 검증
- [ ] Task 9: 엔드투엔드 통합 테스트
- [ ] Task 10: 문서 및 운영 가이드 작성
- [ ] Task 11: 최종 검증 및 정리

## 라이선스

이 프로젝트는 개인 사용을 위한 것입니다.
