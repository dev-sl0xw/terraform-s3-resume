# 구현 계획: Resume Hosting Infrastructure

## 개요

본 구현 계획은 Terraform을 사용하여 AWS에서 PDF 이력서를 호스팅하는 인프라를 구축합니다. S3, CloudFront, Route53, ACM을 사용하여 안전하고 빠르며 비용 효율적인 이력서 호스팅 솔루션을 제공합니다.

## 작업 목록

- [x] 1. Terraform 프로젝트 구조 및 기본 구성 설정
  - Terraform 프로젝트 디렉토리 구조 생성
  - providers.tf 파일 작성 (AWS 프로바이더 구성, us-east-1 alias 포함)
  - variables.tf 파일 작성 (모든 입력 변수 정의 및 검증 규칙)
  - outputs.tf 파일 작성 (S3, CloudFront, Route53 출력 값)
  - terraform.tfvars.example 파일 생성 (변수 예제)
  - .gitignore 파일 생성 (terraform.tfvars, .terraform/, *.tfstate 포함)
  - _요구사항: 5.1, 5.3, 5.5_

- [x] 2. S3 버킷 리소스 구현
  - [x] 2.1 S3 버킷 생성 및 기본 구성
    - s3.tf 파일 생성
    - aws_s3_bucket 리소스 정의 (버킷 이름, 태그)
    - aws_s3_bucket_versioning 리소스 정의 (버전 관리 활성화)
    - aws_s3_bucket_public_access_block 리소스 정의 (모든 공개 접근 차단)
    - _요구사항: 1.1, 1.3, 1.5_
  
  - [x] 2.2 S3 버킷 구성 검증 테스트 작성
    - S3 버킷 존재 확인 테스트
    - 버전 관리 활성화 확인 테스트
    - 공개 접근 차단 확인 테스트
    - _요구사항: 1.1, 1.3, 1.5_
  
  - [x] 2.3 S3 메타데이터 보존 속성 테스트 작성
    - **속성 1: S3 업로드 메타데이터 보존**
    - **검증: 요구사항 1.2**
    - hypothesis를 사용하여 임의의 PDF 파일 생성
    - S3 업로드 후 Content-Type 및 메타데이터 확인
    - 최소 100회 반복 실행

- [x] 3. CloudFront Origin Access Control 및 S3 버킷 정책 구현
  - [x] 3.1 Origin Access Control 생성
    - cloudfront.tf 파일 생성
    - aws_cloudfront_origin_access_control 리소스 정의
    - signing_behavior를 "always"로, signing_protocol을 "sigv4"로 설정
    - _요구사항: 2.4, 7.2_
  
  - [x] 3.2 S3 버킷 정책 구성
    - s3.tf에 aws_s3_bucket_policy 리소스 추가
    - CloudFront Service Principal만 허용하는 정책 작성
    - AWS:SourceArn 조건으로 특정 CloudFront 배포만 허용
    - _요구사항: 2.4, 7.2_
  
  - [x] 3.3 OAC 및 버킷 정책 검증 테스트
    - OAC 리소스 생성 확인
    - S3 직접 접근 차단 확인 (403 응답)
    - _요구사항: 2.4, 7.2_

- [ ] 4. ACM SSL 인증서 프로비저닝
  - [ ] 4.1 ACM 인증서 생성 및 검증
    - acm.tf 파일 생성
    - us-east-1 리전에 aws_acm_certificate 리소스 정의
    - DNS 검증 방식 사용
    - aws_acm_certificate_validation 리소스로 자동 검증
    - _요구사항: 3.2, 3.5_
  
  - [ ] 4.2 Route53 인증서 검증 레코드 생성
    - route53.tf 파일 생성
    - data source로 기존 Route53 호스팅 영역 조회
    - for_each로 ACM 검증 레코드 자동 생성
    - _요구사항: 3.2_
  
  - [ ]* 4.3 ACM 인증서 검증 테스트
    - 인증서가 us-east-1에 생성되었는지 확인
    - 인증서 상태가 "ISSUED"인지 확인
    - 올바른 도메인에 대해 발급되었는지 확인
    - _요구사항: 3.2, 3.5_

- [ ] 5. CloudFront 배포 구성
  - [ ] 5.1 CloudFront 배포 리소스 정의
    - cloudfront.tf에 aws_cloudfront_distribution 리소스 추가
    - S3를 오리진으로 설정 (OAC 사용)
    - 커스텀 도메인 aliases 설정
    - default_root_object를 resume.pdf로 설정
    - _요구사항: 2.1, 2.2, 4.5_
  
  - [ ] 5.2 CloudFront 캐싱 및 보안 설정
    - default_cache_behavior 구성 (GET, HEAD, OPTIONS 허용)
    - viewer_protocol_policy를 "redirect-to-https"로 설정
    - 압축 활성화 (compress = true)
    - TTL 설정 (default 24시간, max 1년)
    - _요구사항: 2.3, 3.1, 3.4_
  
  - [ ] 5.3 CloudFront SSL 및 비용 최적화 설정
    - viewer_certificate에 ACM 인증서 연결
    - ssl_support_method를 "sni-only"로 설정
    - minimum_protocol_version을 "TLSv1.2_2021"로 설정
    - price_class를 "PriceClass_100"으로 설정 (북미, 유럽만)
    - _요구사항: 3.3, 8.4_
  
  - [ ]* 5.4 CloudFront 배포 검증 테스트
    - CloudFront 배포 생성 확인
    - OAC가 올바르게 연결되었는지 확인
    - Price Class가 PriceClass_100인지 확인
    - SSL 설정 확인
    - _요구사항: 2.1, 2.4, 3.3, 8.4_

- [ ] 6. Checkpoint - 기본 인프라 검증
  - 모든 테스트가 통과하는지 확인하고, 질문이 있으면 사용자에게 문의합니다.

- [ ] 7. Route53 DNS 레코드 구성
  - [ ] 7.1 커스텀 도메인 A 레코드 생성
    - route53.tf에 aws_route53_record 리소스 추가
    - A 레코드 Alias로 CloudFront 배포 연결
    - evaluate_target_health를 false로 설정
    - _요구사항: 4.1, 4.2_
  
  - [ ]* 7.2 DNS 레코드 검증 테스트
    - Route53 A 레코드 생성 확인
    - DNS 조회로 CloudFront 도메인 반환 확인
    - _요구사항: 4.1, 4.2_

- [ ] 8. Terraform 멱등성 및 구성 검증
  - [ ]* 8.1 Terraform 멱등성 속성 테스트 작성
    - **속성 2: Terraform 구성 멱등성**
    - **검증: 요구사항 5.2**
    - hypothesis를 사용하여 임의의 변수 조합 생성
    - terraform apply를 두 번 실행하여 두 번째 실행에서 변경 사항 없음 확인
    - 최소 100회 반복 실행
  
  - [ ]* 8.2 Terraform 구성 검증 테스트
    - terraform validate 성공 확인
    - terraform plan 출력 검토
    - 모든 필수 리소스 정의 확인
    - 변수 검증 규칙 테스트
    - _요구사항: 5.1, 5.3_

- [ ] 9. 엔드투엔드 통합 테스트
  - [ ]* 9.1 HTTPS 접근 및 리디렉션 테스트
    - HTTP 요청이 HTTPS로 리디렉션되는지 확인
    - HTTPS 요청이 200 응답을 반환하는지 확인
    - SSL 인증서가 유효한지 확인
    - _요구사항: 3.1, 3.4, 3.5, 4.4_
  
  - [ ]* 9.2 커스텀 도메인 통합 테스트
    - 커스텀 도메인으로 HTTPS 요청
    - Content-Type이 application/pdf인지 확인
    - 이력서 PDF 파일이 반환되는지 확인
    - _요구사항: 4.3, 7.1, 7.3_
  
  - [ ]* 9.3 공개 접근 제어 테스트
    - CloudFront URL로 인증 없이 접근 가능 확인
    - S3 직접 URL로 접근 차단 확인 (403)
    - 존재하지 않는 경로 접근 차단 확인
    - _요구사항: 7.1, 7.2, 7.5_

- [ ] 10. 문서 및 운영 가이드 작성
  - [ ] 10.1 README.md 작성
    - 프로젝트 개요 및 아키텍처 설명
    - 사전 요구사항 (AWS 계정, Terraform, Route53 호스팅 영역)
    - 초기 배포 단계별 가이드
    - 이력서 업데이트 프로세스 상세 설명
    - 캐시 무효화 명령 포함
    - _요구사항: 6.4_
  
  - [ ] 10.2 비용 최적화 및 모니터링 가이드 추가
    - AWS 프리 티어 한도 설명
    - 예상 월간 비용 계산
    - AWS Budgets 설정 가이드
    - CloudWatch 메트릭 모니터링 방법
    - 문제 해결 섹션
    - _요구사항: 8.10_
  
  - [ ] 10.3 terraform.tfvars.example 상세 작성
    - 모든 변수에 대한 예제 값 제공
    - 각 변수에 대한 설명 주석 추가
    - 프리 티어 최적화 권장 사항 포함

- [ ] 11. 최종 검증 및 정리
  - [ ]* 11.1 전체 배포 테스트
    - terraform init, validate, plan, apply 순차 실행
    - 모든 리소스 생성 확인
    - 출력 값 확인
    - 이력서 업로드 및 접근 테스트
    - _요구사항: 5.2, 6.1, 6.5_
  
  - [ ]* 11.2 Terraform destroy 테스트
    - terraform destroy 실행
    - 모든 리소스 삭제 확인
    - AWS 콘솔에서 리소스 부재 확인
    - _요구사항: 5.4_
  
  - [ ]* 11.3 최소 리소스 구성 검증
    - S3 불필요한 기능 비활성화 확인 (분석, 복제, 수명 주기)
    - CloudFront 로깅 비활성화 확인
    - 필수 리소스만 생성되었는지 확인
    - _요구사항: 8.7, 8.8_

- [ ] 12. Checkpoint - 최종 검증
  - 모든 테스트가 통과하는지 확인하고, 질문이 있으면 사용자에게 문의합니다.

## 참고사항

- "*" 표시가 있는 작업은 선택 사항으로, 핵심 기능에 먼저 집중하기 위해 건너뛸 수 있습니다
- 각 작업은 특정 요구사항을 참조하여 추적 가능성을 보장합니다
- Checkpoint 작업은 점진적 검증을 위한 중간 확인 지점입니다
- 속성 기반 테스트는 최소 100회 반복 실행으로 구성됩니다
- 모든 Terraform 코드는 HCL(HashiCorp Configuration Language)로 작성됩니다
