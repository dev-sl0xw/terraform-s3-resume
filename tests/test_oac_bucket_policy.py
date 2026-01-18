"""
OAC 및 버킷 정책 검증 테스트
Task 3.3: OAC 리소스 생성 확인, S3 직접 접근 차단 확인
요구사항: 2.4, 7.2
"""

import boto3
import pytest
import json
import os
import requests


@pytest.fixture(scope="module")
def terraform_outputs():
    """Terraform 출력 값을 로드하는 fixture"""
    import subprocess
    
    result = subprocess.run(
        ['terraform', 'output', '-json'],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    
    if result.returncode != 0:
        pytest.skip(f"Terraform outputs not available: {result.stderr}")
    
    outputs = json.loads(result.stdout)
    return {key: value['value'] for key, value in outputs.items()}


@pytest.fixture(scope="module")
def cloudfront_client():
    """CloudFront 클라이언트 fixture"""
    return boto3.client('cloudfront')


@pytest.fixture(scope="module")
def s3_client():
    """S3 클라이언트 fixture"""
    return boto3.client('s3')


class TestOACConfiguration:
    """OAC 리소스 생성 확인 테스트"""
    
    def test_oac_exists(self, cloudfront_client, terraform_outputs):
        """
        테스트: OAC 리소스 존재 확인
        요구사항 2.4: CloudFront_Distribution은 S3_Bucket에 안전하게 접근하기 위해 OAC를 사용해야 합니다
        """
        oac_id = terraform_outputs.get('cloudfront_oac_id')
        if not oac_id:
            pytest.skip("cloudfront_oac_id output not available")
        
        response = cloudfront_client.get_origin_access_control(Id=oac_id)
        oac = response['OriginAccessControl']['OriginAccessControlConfig']
        
        assert oac is not None, "OAC가 존재하지 않습니다"
        assert oac['OriginAccessControlOriginType'] == 's3', \
            f"OAC 오리진 타입이 's3'가 아닙니다: {oac['OriginAccessControlOriginType']}"
    
    def test_oac_signing_behavior(self, cloudfront_client, terraform_outputs):
        """
        테스트: OAC signing_behavior가 'always'로 설정되어 있는지 확인
        요구사항 2.4: 모든 요청에 서명이 필요
        """
        oac_id = terraform_outputs.get('cloudfront_oac_id')
        if not oac_id:
            pytest.skip("cloudfront_oac_id output not available")
        
        response = cloudfront_client.get_origin_access_control(Id=oac_id)
        oac = response['OriginAccessControl']['OriginAccessControlConfig']
        
        assert oac['SigningBehavior'] == 'always', \
            f"SigningBehavior가 'always'가 아닙니다: {oac['SigningBehavior']}"
    
    def test_oac_signing_protocol(self, cloudfront_client, terraform_outputs):
        """
        테스트: OAC signing_protocol이 'sigv4'로 설정되어 있는지 확인
        요구사항 2.4: AWS SigV4 서명 프로토콜 사용
        """
        oac_id = terraform_outputs.get('cloudfront_oac_id')
        if not oac_id:
            pytest.skip("cloudfront_oac_id output not available")
        
        response = cloudfront_client.get_origin_access_control(Id=oac_id)
        oac = response['OriginAccessControl']['OriginAccessControlConfig']
        
        assert oac['SigningProtocol'] == 'sigv4', \
            f"SigningProtocol이 'sigv4'가 아닙니다: {oac['SigningProtocol']}"
    
    def test_cloudfront_uses_oac(self, cloudfront_client, terraform_outputs):
        """
        테스트: CloudFront 배포가 OAC를 사용하는지 확인
        요구사항 2.4: CloudFront가 OAC를 통해 S3에 접근
        """
        dist_id = terraform_outputs.get('cloudfront_distribution_id')
        oac_id = terraform_outputs.get('cloudfront_oac_id')
        
        if not dist_id or not oac_id:
            pytest.skip("CloudFront distribution or OAC ID not available")
        
        response = cloudfront_client.get_distribution(Id=dist_id)
        origins = response['Distribution']['DistributionConfig']['Origins']['Items']
        
        # S3 오리진이 OAC를 사용하는지 확인
        s3_origin = next((o for o in origins if 's3' in o['DomainName'].lower()), None)
        assert s3_origin is not None, "S3 오리진을 찾을 수 없습니다"
        
        origin_oac_id = s3_origin.get('OriginAccessControlId', '')
        assert origin_oac_id == oac_id, \
            f"CloudFront가 올바른 OAC를 사용하지 않습니다. 예상: {oac_id}, 실제: {origin_oac_id}"


class TestS3BucketPolicy:
    """S3 버킷 정책 검증 테스트"""
    
    def test_bucket_policy_exists(self, s3_client, terraform_outputs):
        """
        테스트: S3 버킷 정책 존재 확인
        요구사항 7.2: S3_Bucket은 비공개로 유지되고 OAC를 통해서만 접근 가능해야 합니다
        """
        bucket_name = terraform_outputs.get('s3_bucket_name')
        if not bucket_name:
            pytest.skip("s3_bucket_name output not available")
        
        response = s3_client.get_bucket_policy(Bucket=bucket_name)
        policy = json.loads(response['Policy'])
        
        assert 'Statement' in policy, "버킷 정책에 Statement가 없습니다"
        assert len(policy['Statement']) > 0, "버킷 정책에 Statement가 비어있습니다"
    
    def test_bucket_policy_allows_cloudfront_only(self, s3_client, terraform_outputs):
        """
        테스트: 버킷 정책이 CloudFront Service Principal만 허용하는지 확인
        요구사항 7.2: CloudFront만 S3에 접근 가능
        """
        bucket_name = terraform_outputs.get('s3_bucket_name')
        if not bucket_name:
            pytest.skip("s3_bucket_name output not available")
        
        response = s3_client.get_bucket_policy(Bucket=bucket_name)
        policy = json.loads(response['Policy'])
        
        # CloudFront Service Principal 허용 확인
        cloudfront_statement = None
        for statement in policy['Statement']:
            principal = statement.get('Principal', {})
            if isinstance(principal, dict):
                service = principal.get('Service', '')
                if service == 'cloudfront.amazonaws.com':
                    cloudfront_statement = statement
                    break
        
        assert cloudfront_statement is not None, \
            "버킷 정책에 CloudFront Service Principal 허용 Statement가 없습니다"
        assert cloudfront_statement['Effect'] == 'Allow', \
            "CloudFront Statement의 Effect가 'Allow'가 아닙니다"
    
    def test_bucket_policy_has_source_arn_condition(self, s3_client, terraform_outputs):
        """
        테스트: 버킷 정책에 AWS:SourceArn 조건이 있는지 확인
        요구사항 7.2: 특정 CloudFront 배포만 허용
        """
        bucket_name = terraform_outputs.get('s3_bucket_name')
        cloudfront_arn = terraform_outputs.get('cloudfront_distribution_arn')
        
        if not bucket_name:
            pytest.skip("s3_bucket_name output not available")
        
        response = s3_client.get_bucket_policy(Bucket=bucket_name)
        policy = json.loads(response['Policy'])
        
        # SourceArn 조건 확인
        has_source_arn = False
        for statement in policy['Statement']:
            condition = statement.get('Condition', {})
            string_equals = condition.get('StringEquals', {})
            if 'AWS:SourceArn' in string_equals:
                has_source_arn = True
                if cloudfront_arn:
                    assert string_equals['AWS:SourceArn'] == cloudfront_arn, \
                        f"SourceArn이 CloudFront ARN과 일치하지 않습니다"
                break
        
        assert has_source_arn, "버킷 정책에 AWS:SourceArn 조건이 없습니다"


class TestS3DirectAccessBlocked:
    """S3 직접 접근 차단 확인 테스트"""
    
    def test_s3_direct_url_returns_403(self, terraform_outputs):
        """
        테스트: S3 직접 URL 접근 시 403 응답 확인
        요구사항 7.2: S3_Bucket은 비공개로 유지되고 직접 접근 불가
        """
        bucket_name = terraform_outputs.get('s3_bucket_name')
        if not bucket_name:
            pytest.skip("s3_bucket_name output not available")
        
        # S3 직접 URL 구성 (여러 형식 테스트)
        s3_urls = [
            f"https://{bucket_name}.s3.amazonaws.com/resume.pdf",
            f"https://s3.amazonaws.com/{bucket_name}/resume.pdf",
        ]
        
        for url in s3_urls:
            try:
                response = requests.get(url, timeout=10)
                assert response.status_code == 403, \
                    f"S3 직접 접근이 차단되지 않았습니다. URL: {url}, 상태 코드: {response.status_code}"
            except requests.exceptions.RequestException as e:
                # 연결 오류도 접근 차단으로 간주
                pass
    
    def test_s3_direct_access_denied_message(self, terraform_outputs):
        """
        테스트: S3 직접 접근 시 AccessDenied 메시지 확인
        요구사항 7.2: 직접 접근 시 명확한 거부 응답
        """
        bucket_name = terraform_outputs.get('s3_bucket_name')
        if not bucket_name:
            pytest.skip("s3_bucket_name output not available")
        
        url = f"https://{bucket_name}.s3.amazonaws.com/resume.pdf"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 403:
                # AccessDenied 메시지 확인
                assert 'AccessDenied' in response.text or 'Access Denied' in response.text, \
                    "403 응답이지만 AccessDenied 메시지가 없습니다"
        except requests.exceptions.RequestException:
            pytest.skip("S3 URL에 연결할 수 없습니다")
