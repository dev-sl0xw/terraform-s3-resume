# 구현 계획: Resume Hosting Infrastructure

## 개요

Terraform을 사용하여 AWS에서 PDF 이력서를 호스팅하는 인프라를 구축합니다. S3, CloudFront, ACM을 사용하여 안전하고 빠르며 비용 효율적인 이력서 호스팅 솔루션을 제공합니다.

> **참고**: Route53은 사용하지 않습니다. 지인의 도메인에서 서브도메인을 빌려 사용하고 있어, DNS 레코드는 지인의 DNS 서버에서 수동으로 관리합니다.

## 작업 목록

- [x] 1. Terraform 프로젝트 구조 및 기본 구성 설정
  - Terraform 프로젝트 디렉토리 구조 생성
  - providers.tf, variables.tf, outputs.tf 파일 작성
  - terraform.tfvars.example, .gitignore 파일 생성

- [x] 2. S3 버킷 리소스 구현
  - S3 버킷 생성 및 기본 구성 (s3.tf)
  - 버전 관리 활성화, 공개 접근 차단
  - S3 버킷 구성 검증 테스트 작성

- [x] 3. CloudFront Origin Access Control 및 S3 버킷 정책 구현
  - Origin Access Control 생성 (cloudfront.tf)
  - S3 버킷 정책 구성 (CloudFront만 접근 허용)
  - OAC 및 버킷 정책 검증 테스트

- [x] 4. ACM SSL 인증서 프로비저닝
  - ACM 인증서 생성 (us-east-1, acm.tf)
  - DNS 검증 완료 (지인 DNS 서버에서 수동 CNAME 추가)
  - 인증서 상태: ISSUED

- [x] 5. CloudFront 배포 구성
  - CloudFront 배포 리소스 정의 (S3 오리진, OAC 사용)
  - 커스텀 도메인 aliases 설정 (slow0x.er.ht)
  - HTTPS 리디렉션, ACM 인증서 연결
  - TLSv1.2_2021, SNI-only 설정

- [x] 6. 기본 인프라 검증 완료
  - https://slow0x.er.ht/ 로 이력서 접근 확인
  - SSL 인증서 정상 작동 확인

## 완료된 인프라

| 리소스 | 상태 | 비고 |
|--------|------|------|
| S3 버킷 | ✅ | resume-hosting-test-20260118 |
| CloudFront | ✅ | E27JDTW678QD8T |
| ACM 인증서 | ✅ | us-east-1, ISSUED |
| 커스텀 도메인 | ✅ | https://slow0x.er.ht/ |
| HTTPS | ✅ | TLSv1.2_2021 |

## 참고사항

- Route53은 사용하지 않음 (지인 DNS 서버에서 수동 관리)
- DNS 레코드: ACM 검증용 CNAME, CloudFront 연결용 CNAME
- 모든 Terraform 코드는 HCL로 작성됨
