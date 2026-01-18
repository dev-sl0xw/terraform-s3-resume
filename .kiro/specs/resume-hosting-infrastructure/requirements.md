# 요구사항 문서

## 소개

본 문서는 AWS에서 PDF 이력서를 호스팅하는 Terraform 기반 인프라의 요구사항을 명시합니다. 이 시스템은 채용 담당자와 실무진이 커스텀 도메인을 통해 HTTPS 보안과 CloudFront CDN을 통한 빠른 콘텐츠 전송으로 이력서에 접근할 수 있도록 합니다.

## 용어 정의

- **Resume_Hosting_System**: PDF 이력서를 제공하는 전체 인프라 스택
- **S3_Bucket**: PDF 이력서 파일을 저장하는 AWS Simple Storage Service 버킷
- **CloudFront_Distribution**: 이력서를 전 세계적으로 캐싱하고 제공하는 AWS Content Delivery Network
- **Custom_Domain**: CloudFront 배포를 가리키는 사용자 제공 도메인 이름 (예: resume.yourdomain.com)
- **SSL_Certificate**: HTTPS 암호화를 위한 AWS Certificate Manager의 TLS/SSL 인증서
- **Terraform_Configuration**: AWS 리소스를 정의하고 프로비저닝하는 Infrastructure as Code 파일
- **Route53_Record**: 커스텀 도메인을 CloudFront에 매핑하는 DNS 레코드
- **Origin_Access_Identity**: 버킷을 공개하지 않고 S3에 안전하게 접근하는 CloudFront 자격 증명
- **Portfolio_Site**: Astro로 개발된 반응형 정적 웹사이트로, GitHub 링크, 아키텍처 다이어그램, 이력서 다운로드 기능을 제공. 기존 S3_Bucket에 함께 저장됨

## 요구사항

### 요구사항 1: 이력서를 위한 S3 스토리지

**사용자 스토리:** 이력서 소유자로서, PDF 이력서를 S3에 저장하여 안정적으로 호스팅하고 쉽게 업데이트할 수 있기를 원합니다.

#### 수락 기준

1. S3_Bucket은 PDF 이력서 파일을 저장해야 합니다
2. 이력서 PDF가 S3에 업로드되면, S3_Bucket은 적절한 메타데이터와 함께 파일을 보관해야 합니다
3. S3_Bucket은 비공개 접근으로 구성되어야 합니다 (공개적으로 접근 불가)
4. 새로운 이력서 버전이 업로드되면, S3_Bucket은 기존 파일을 교체해야 합니다
5. S3_Bucket은 이력서 업데이트를 추적하기 위해 버전 관리를 활성화해야 합니다

### 요구사항 2: CloudFront 콘텐츠 전송

**사용자 스토리:** 채용 담당자로서, 어느 위치에서든 이력서에 빠르게 접근하여 지원자의 자격을 신속하게 검토할 수 있기를 원합니다.

#### 수락 기준

1. CloudFront_Distribution은 전 세계 엣지 로케이션에서 이력서 PDF를 제공해야 합니다
2. CloudFront URL로 요청이 들어오면, CloudFront_Distribution은 S3_Bucket에서 이력서를 가져와야 합니다
3. CloudFront_Distribution은 성능 향상을 위해 엣지 로케이션에 이력서를 캐싱해야 합니다
4. CloudFront_Distribution은 S3_Bucket에 안전하게 접근하기 위해 Origin_Access_Identity를 사용해야 합니다
5. S3에서 이력서가 업데이트되면, CloudFront_Distribution은 캐시 무효화를 지원해야 합니다

### 요구사항 3: HTTPS 보안

**사용자 스토리:** 채용 담당자로서, HTTPS를 통해 이력서에 접근하여 연결이 안전하고 신뢰할 수 있기를 원합니다.

#### 수락 기준

1. Resume_Hosting_System은 모든 이력서 접근 요청에 대해 HTTPS를 강제해야 합니다
2. SSL_Certificate는 Custom_Domain을 위해 AWS Certificate Manager를 통해 프로비저닝되어야 합니다
3. CloudFront_Distribution은 HTTPS 연결을 위해 SSL_Certificate를 사용해야 합니다
4. 사용자가 HTTP를 통해 이력서에 접근하면, CloudFront_Distribution은 HTTPS로 리디렉션해야 합니다
5. SSL_Certificate는 표준 웹 브라우저에서 유효하고 신뢰할 수 있어야 합니다

### 요구사항 4: 커스텀 도메인 통합

**사용자 스토리:** 이력서 소유자로서, 채용 담당자가 기억하기 쉬운 커스텀 도메인을 통해 이력서에 접근하여 전문적으로 보이고 공유하기 쉽기를 원합니다.

#### 수락 기준

1. Custom_Domain은 CNAME 레코드를 통해 CloudFront_Distribution을 가리켜야 합니다
2. Route53_Record는 Custom_Domain을 CloudFront 배포 도메인에 매핑해야 합니다
3. 사용자가 Custom_Domain을 방문하면, Resume_Hosting_System은 이력서 PDF를 제공해야 합니다
4. Custom_Domain은 유효한 SSL 인증서로 HTTPS를 지원해야 합니다
5. CloudFront_Distribution은 Custom_Domain에 대한 요청을 수락해야 합니다

### 요구사항 5: Terraform을 사용한 Infrastructure as Code

**사용자 스토리:** DevOps 엔지니어로서, Terraform을 사용하여 인프라를 정의하여 재현 가능하고 버전 관리되며 유지보수 가능하기를 원합니다.

#### 수락 기준

1. Terraform_Configuration은 모든 AWS 리소스(S3, CloudFront, Route53, ACM)를 정의해야 합니다
2. Terraform apply가 실행되면, Terraform_Configuration은 필요한 모든 인프라를 프로비저닝해야 합니다
3. Terraform_Configuration은 구성 가능한 값(도메인 이름, 리전, 버킷 이름)에 대해 변수를 사용해야 합니다
4. Terraform destroy가 실행되면, Terraform_Configuration은 프로비저닝된 모든 리소스를 제거해야 합니다
5. Terraform_Configuration은 프로비저닝 후 CloudFront URL과 커스텀 도메인 URL을 출력해야 합니다

### 요구사항 6: 이력서 업데이트 프로세스

**사용자 스토리:** 이력서 소유자로서, 이력서 PDF를 쉽게 업데이트하여 채용 담당자가 항상 최신 버전을 볼 수 있기를 원합니다.

#### 수락 기준

1. 새로운 이력서 PDF가 S3_Bucket에 업로드되면, Resume_Hosting_System은 Custom_Domain을 통해 이를 제공해야 합니다
2. Resume_Hosting_System은 이력서 업데이트 후 CloudFront 캐시를 무효화하는 메커니즘을 제공해야 합니다
3. 캐시 무효화가 트리거되면, CloudFront_Distribution은 S3에서 업데이트된 이력서를 가져와야 합니다
4. Terraform_Configuration은 이력서 업데이트 프로세스에 대한 문서를 포함해야 합니다
5. S3_Bucket은 AWS CLI 또는 Console을 통한 이력서 업로드를 수락해야 합니다

### 요구사항 7: 공개 접근 제어

**사용자 스토리:** 이력서 소유자로서, 채용 담당자가 인증 없이 이력서에 접근하여 채용 과정에서 쉽게 볼 수 있기를 원합니다.

#### 수락 기준

1. CloudFront_Distribution은 이력서 PDF에 대한 공개 읽기 접근을 허용해야 합니다
2. S3_Bucket은 비공개로 유지되고 Origin_Access_Identity를 통해서만 접근 가능해야 합니다
3. 사용자가 Custom_Domain을 요청하면, Resume_Hosting_System은 자격 증명 없이 이력서를 제공해야 합니다
4. CloudFront_Distribution은 서명된 URL이나 인증 토큰을 요구하지 않아야 합니다
5. Resume_Hosting_System은 이력서 PDF만 제공하고 다른 S3 콘텐츠를 노출하지 않아야 합니다

### 요구사항 8: AWS 프리 티어 범위 내 비용 최적화

**사용자 스토리:** 이력서 소유자로서, AWS 프리 티어 범위 내에서 인프라를 구축하여 MVP로 이력서 호스팅이 무료 또는 최소 비용으로 가능하기를 원합니다.

#### 수락 기준

1. S3_Bucket은 AWS 프리 티어 한도(5GB 스토리지, 20,000 GET 요청, 2,000 PUT 요청/월) 내에서 작동해야 합니다
2. S3_Bucket은 단일 PDF 파일에 대해 Standard 스토리지 클래스를 사용해야 합니다
3. CloudFront_Distribution은 AWS 프리 티어 한도(1TB 데이터 전송, 10,000,000 HTTP/HTTPS 요청/월) 내에서 작동해야 합니다
4. CloudFront_Distribution은 비용 효율적인 글로벌 전송을 위해 기본 가격 클래스를 사용해야 합니다
5. Route53은 호스팅 영역 비용($0.50/월)만 발생하며, 쿼리는 프리 티어 한도(100만 쿼리/월) 내에서 작동해야 합니다
6. ACM(AWS Certificate Manager) SSL 인증서는 무료로 제공되어야 합니다
7. Terraform_Configuration은 불필요한 리소스 프로비저닝을 피해야 합니다
8. S3_Bucket은 추가 비용이 발생하는 불필요한 기능(예: 분석, 복제, 수명 주기 정책)을 활성화하지 않아야 합니다
9. Resume_Hosting_System은 프리 티어 한도 초과를 방지하기 위해 최소한의 리소스만 사용해야 합니다
10. Terraform_Configuration은 프리 티어 사용량을 모니터링할 수 있는 가이드를 문서에 포함해야 합니다

### 요구사항 9: 포트폴리오 정적 사이트 확장 (단일 버킷 방식)

**사용자 스토리:** 이력서 소유자로서, 포트폴리오 정적 사이트를 통해 프로젝트 정보, 아키텍처, 이력서 파일들을 한 곳에서 보여주어 채용 담당자가 나의 기술 역량을 종합적으로 확인할 수 있기를 원합니다.

#### 수락 기준 9

1. 기존 S3_Bucket에 Astro 빌드 결과물(정적 파일)과 이력서 PDF를 함께 저장해야 합니다
2. Portfolio_Site는 이 프로젝트의 GitHub Repository URL을 표시해야 합니다
3. Portfolio_Site는 프로젝트 아키텍처 다이어그램(architecture diagram)을 표시해야 합니다
4. Portfolio_Site는 이력서 PDF 파일 다운로드 링크를 제공해야 합니다
5. 기존 CloudFront_Distribution의 default_root_object를 index.html로 변경해야 합니다
6. CloudFront_Distribution은 SPA 라우팅을 위한 커스텀 에러 응답(404 → index.html)을 설정해야 합니다
7. Portfolio_Site는 Astro로 개발되고 반응형 디자인으로 모바일과 데스크톱에서 모두 최적화되어야 합니다
8. 기존 커스텀 도메인(slow0x.er.ht)으로 포트폴리오 사이트에 접근 가능해야 합니다
9. 이력서 PDF는 /resume.pdf 경로로 계속 접근 가능해야 합니다
10. Portfolio_Site는 AWS 프리 티어 범위 내에서 운영되어야 합니다 (추가 리소스 없음)
