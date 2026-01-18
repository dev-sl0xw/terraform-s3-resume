# Resume Hosting Infrastructure 아키텍처

## 전체 아키텍처 구성도

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Resume Hosting Infrastructure                          │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────┐
                                    │   사용자      │
                                    │ (채용담당자)  │
                                    └──────┬───────┘
                                           │
                                           │ HTTPS 요청
                                           │ resume.yourdomain.com
                                           ▼
                              ┌────────────────────────┐
                              │      Route53           │
                              │    (DNS 레코드)        │
                              │                        │
                              │  A Record (Alias)      │
                              └───────────┬────────────┘
                                          │
                                          │ DNS 해석
                                          ▼
┌─────────────────┐          ┌────────────────────────┐
│      ACM        │─────────▶│     CloudFront         │
│  (SSL 인증서)   │  SSL/TLS │    Distribution        │
│                 │          │                        │
│ us-east-1 리전  │          │ • HTTPS 강제           │
│ DNS 검증        │          │ • 캐싱 (24시간 TTL)    │
└─────────────────┘          │ • PriceClass_100       │
                              │ • 압축 활성화          │
                              └───────────┬────────────┘
                                          │
                                          │ OAC 인증
                                          ▼
                              ┌────────────────────────┐
                              │  Origin Access Control │
                              │        (OAC)           │
                              │                        │
                              │  SigV4 서명 인증       │
                              └───────────┬────────────┘
                                          │
                                          │ 보안 접근
                                          ▼
                              ┌────────────────────────┐
                              │      S3 Bucket         │
                              │   (비공개 스토리지)    │
                              │                        │
                              │ • 버전 관리 활성화     │
                              │ • 공개 접근 차단       │
                              │ • Standard 스토리지    │
                              │ • resume.pdf 저장      │
                              └────────────────────────┘
```

## AWS 컴포넌트 목록

| 컴포넌트 | AWS 서비스 | 역할 | 관리 방식 |
|---------|-----------|------|----------|
| Route53 | Amazon Route 53 | DNS 관리, A Record Alias | 수동 등록 (Terraform 외부) |
| ACM | AWS Certificate Manager | SSL/TLS 인증서 (us-east-1) | Terraform |
| CloudFront | Amazon CloudFront | CDN, HTTPS 강제, 캐싱 | Terraform |
| OAC | CloudFront Origin Access Control | S3 보안 접근 제어 | Terraform |
| S3 | Amazon S3 | PDF 이력서 저장 (비공개) | Terraform |

> **참고**: Route53 호스팅 영역 및 DNS 레코드는 수동으로 등록되었으며, Terraform으로 관리되지 않습니다.

## 데이터 흐름

```
[사용자] ──HTTPS──▶ [Route53] ──DNS──▶ [CloudFront] ──OAC──▶ [S3]
                                            │
                                       [ACM 인증서]
```

1. 사용자가 `resume.yourdomain.com`으로 HTTPS 요청
2. Route53이 CloudFront 도메인으로 DNS 해석
3. CloudFront가 ACM 인증서로 HTTPS 처리
4. CloudFront 캐시 확인 (히트 시 바로 응답)
5. 캐시 미스 시 OAC 인증으로 S3 접근
6. S3에서 PDF 파일 반환
7. CloudFront가 사용자에게 HTTPS로 응답

## 보안 구성

| 구성 요소 | 보안 설정 |
|----------|----------|
| S3 Bucket | 모든 공개 접근 차단, CloudFront OAC만 접근 허용 |
| CloudFront | HTTP → HTTPS 자동 리디렉션, TLS 1.2 이상 |
| ACM | DNS 검증 방식, 자동 갱신 |
| OAC | AWS SigV4 서명 인증 |

## 비용 최적화

| 서비스 | 프리 티어 한도 | 설정 | 비고 |
|-------|---------------|------|------|
| S3 | 5GB 스토리지, 20,000 GET/월 | Standard 스토리지 클래스 | Terraform 관리 |
| CloudFront | 1TB 전송, 10M 요청/월 | PriceClass_100 (북미, 유럽) | Terraform 관리 |
| Route53 | 100만 쿼리/월 | 호스팅 영역 $0.50/월 | 수동 등록 |
| ACM | 무료 | 공개 인증서 | Terraform 관리 |

## draw.io 작성 가이드

AWS Architecture Icons 다운로드: https://aws.amazon.com/architecture/icons/

사용할 아이콘:
- `Arch_Amazon-Route-53_48.svg`
- `Arch_AWS-Certificate-Manager_48.svg`
- `Arch_Amazon-CloudFront_48.svg`
- `Arch_Amazon-Simple-Storage-Service_48.svg`
- `Res_User_48_Light.svg` (사용자)
