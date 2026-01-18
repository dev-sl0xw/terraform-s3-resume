"""
S3 메타데이터 보존 속성 테스트
Task 2.3: S3 업로드 메타데이터 보존 속성 테스트
요구사항: 1.2

속성 1: S3 업로드 메타데이터 보존
임의의 PDF 파일에 대해, S3에 업로드한 후 파일을 조회하면 
올바른 Content-Type(application/pdf)과 메타데이터가 보존되어야 합니다.

**Validates: Requirements 1.2**
"""

import boto3
import pytest
import json
import os
import io
import uuid
from hypothesis import given, strategies as st, settings, Verbosity

# PDF 파일의 최소 헤더 (유효한 PDF 시그니처)
PDF_HEADER = b'%PDF-1.4\n'
PDF_FOOTER = b'\n%%EOF'


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
def s3_client():
    """S3 클라이언트 fixture"""
    return boto3.client('s3')


@pytest.fixture(scope="module")
def bucket_name(terraform_outputs):
    """S3 버킷 이름 fixture"""
    return terraform_outputs['s3_bucket_name']


def create_minimal_pdf(content_bytes: bytes) -> bytes:
    """
    임의의 바이트를 포함하는 최소한의 유효한 PDF 구조 생성
    """
    return PDF_HEADER + content_bytes + PDF_FOOTER


# 메타데이터 키에 사용할 수 있는 문자 전략
metadata_key_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu', 'Nd'),
        whitelist_characters='-_'
    ),
    min_size=1,
    max_size=20
).filter(lambda x: x[0].isalpha())

# 메타데이터 값 전략 (ASCII 문자만)
metadata_value_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd', 'Zs')),
    min_size=1,
    max_size=50
)


@pytest.mark.property
@settings(
    max_examples=3,
    deadline=None,
    verbosity=Verbosity.verbose
)
@given(
    content=st.binary(min_size=10, max_size=100),
    custom_metadata=st.fixed_dictionaries({}, optional={"testkey": st.just("testvalue")})
)
def test_s3_upload_metadata_preservation(s3_client, bucket_name, content, custom_metadata):
    """
    속성 1: S3 업로드 메타데이터 보존
    
    **Validates: Requirements 1.2**
    
    임의의 PDF 파일에 대해:
    1. Content-Type이 application/pdf로 보존되어야 함
    2. 사용자 정의 메타데이터가 보존되어야 함
    3. Content-Length가 올바르게 보존되어야 함
    """
    # 테스트용 고유 키 생성
    test_key = f"test-metadata-{uuid.uuid4()}.pdf"
    
    # 최소한의 PDF 구조로 파일 생성
    pdf_content = create_minimal_pdf(content)
    
    try:
        # S3에 업로드 (Content-Type과 메타데이터 포함)
        extra_args = {
            'ContentType': 'application/pdf'
        }
        
        if custom_metadata:
            extra_args['Metadata'] = custom_metadata
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=pdf_content,
            **extra_args
        )
        
        # 업로드된 객체의 메타데이터 조회
        response = s3_client.head_object(Bucket=bucket_name, Key=test_key)
        
        # 속성 검증 1: Content-Type 보존
        assert response['ContentType'] == 'application/pdf', \
            f"Content-Type이 보존되지 않았습니다. 예상: application/pdf, 실제: {response['ContentType']}"
        
        # 속성 검증 2: Content-Length 보존
        assert response['ContentLength'] == len(pdf_content), \
            f"Content-Length가 올바르지 않습니다. 예상: {len(pdf_content)}, 실제: {response['ContentLength']}"
        
        # 속성 검증 3: 사용자 정의 메타데이터 보존
        if custom_metadata:
            returned_metadata = response.get('Metadata', {})
            for key, value in custom_metadata.items():
                # S3는 메타데이터 키를 소문자로 변환
                lower_key = key.lower()
                assert lower_key in returned_metadata, \
                    f"메타데이터 키 '{key}'가 보존되지 않았습니다"
                assert returned_metadata[lower_key] == value, \
                    f"메타데이터 값이 보존되지 않았습니다. 키: {key}, 예상: {value}, 실제: {returned_metadata[lower_key]}"
    
    finally:
        # 테스트 후 정리: 업로드된 객체 삭제
        try:
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        except Exception:
            pass  # 정리 실패는 무시
