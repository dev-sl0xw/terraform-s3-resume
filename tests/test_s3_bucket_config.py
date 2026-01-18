"""
S3 버킷 구성 검증 테스트
Task 2.2: S3 버킷 존재, 버전 관리, 공개 접근 차단 확인
요구사항: 1.1, 1.3, 1.5
"""

import boto3
import pytest
import json
import os


@pytest.fixture(scope="module")
def terraform_outputs():
    """Terraform 출력 값을 로드하는 fixture"""
    # terraform output -json 명령으로 출력 값 가져오기
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
def s3_client():
    """S3 클라이언트 fixture"""
    return boto3.client('s3')


@pytest.fixture(scope="module")
def bucket_name(terraform_outputs):
    """S3 버킷 이름 fixture"""
    return terraform_outputs['s3_bucket_name']


def test_s3_bucket_exists(s3_client, bucket_name):
    """
    테스트: S3 버킷 존재 확인
    요구사항 1.1: S3_Bucket은 PDF 이력서 파일을 저장해야 합니다
    """
    try:
        response = s3_client.head_bucket(Bucket=bucket_name)
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    except s3_client.exceptions.NoSuchBucket:
        pytest.fail(f"S3 버킷 '{bucket_name}'이 존재하지 않습니다")
    except s3_client.exceptions.ClientError as e:
        pytest.fail(f"S3 버킷 확인 중 오류 발생: {e}")


def test_s3_versioning_enabled(s3_client, bucket_name):
    """
    테스트: 버전 관리 활성화 확인
    요구사항 1.5: S3_Bucket은 이력서 업데이트를 추적하기 위해 버전 관리를 활성화해야 합니다
    """
    try:
        response = s3_client.get_bucket_versioning(Bucket=bucket_name)
        versioning_status = response.get('Status', 'Disabled')
        
        assert versioning_status == 'Enabled', \
            f"버전 관리가 활성화되지 않았습니다. 현재 상태: {versioning_status}"
    except s3_client.exceptions.ClientError as e:
        pytest.fail(f"버전 관리 상태 확인 중 오류 발생: {e}")


def test_s3_public_access_blocked(s3_client, bucket_name):
    """
    테스트: 공개 접근 차단 확인
    요구사항 1.3: S3_Bucket은 비공개 접근으로 구성되어야 합니다 (공개적으로 접근 불가)
    """
    try:
        response = s3_client.get_public_access_block(Bucket=bucket_name)
        config = response['PublicAccessBlockConfiguration']
        
        # 모든 공개 접근 차단 설정이 True여야 함
        assert config['BlockPublicAcls'] is True, \
            "BlockPublicAcls가 활성화되지 않았습니다"
        assert config['BlockPublicPolicy'] is True, \
            "BlockPublicPolicy가 활성화되지 않았습니다"
        assert config['IgnorePublicAcls'] is True, \
            "IgnorePublicAcls가 활성화되지 않았습니다"
        assert config['RestrictPublicBuckets'] is True, \
            "RestrictPublicBuckets가 활성화되지 않았습니다"
            
    except s3_client.exceptions.ClientError as e:
        pytest.fail(f"공개 접근 차단 설정 확인 중 오류 발생: {e}")


def test_s3_bucket_tags(s3_client, bucket_name):
    """
    테스트: S3 버킷 태그 확인 (추가 검증)
    Terraform 구성에서 정의한 태그가 올바르게 적용되었는지 확인
    """
    try:
        response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        tags = {tag['Key']: tag['Value'] for tag in response['TagSet']}
        
        # 필수 태그 확인
        assert 'Name' in tags, "Name 태그가 없습니다"
        assert tags['Name'] == 'Resume Hosting Bucket', \
            f"Name 태그 값이 올바르지 않습니다: {tags['Name']}"
        
        assert 'ManagedBy' in tags, "ManagedBy 태그가 없습니다"
        assert tags['ManagedBy'] == 'Terraform', \
            f"ManagedBy 태그 값이 올바르지 않습니다: {tags['ManagedBy']}"
            
    except s3_client.exceptions.ClientError as e:
        # 태그가 없을 수도 있으므로 경고만 출력
        pytest.skip(f"버킷 태그 확인 중 오류 발생: {e}")
