#!/bin/bash
# S3 버킷 구성 검증 테스트 실행 스크립트

set -e

echo "=========================================="
echo "S3 버킷 구성 검증 테스트"
echo "Task 2.2: 요구사항 1.1, 1.3, 1.5"
echo "=========================================="
echo ""

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Terraform 상태 확인
echo "1. Terraform 상태 확인..."
if ! terraform state list > /dev/null 2>&1; then
    echo "❌ 오류: Terraform 인프라가 배포되지 않았습니다."
    echo ""
    echo "먼저 인프라를 배포하세요:"
    echo "  terraform init"
    echo "  terraform apply"
    exit 1
fi

echo "✓ Terraform 상태 확인 완료"
echo ""

# AWS 자격 증명 확인
echo "2. AWS 자격 증명 확인..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ 오류: AWS 자격 증명이 구성되지 않았습니다."
    echo ""
    echo "AWS 자격 증명을 구성하세요:"
    echo "  export AWS_PROFILE=your-profile"
    echo "  또는"
    echo "  export AWS_ACCESS_KEY_ID=..."
    echo "  export AWS_SECRET_ACCESS_KEY=..."
    exit 1
fi

echo "✓ AWS 자격 증명 확인 완료"
echo ""

# Python 의존성 확인
echo "3. Python 의존성 확인..."
if ! python3 -c "import pytest, boto3" 2>/dev/null; then
    echo "⚠️  경고: 필요한 Python 패키지가 설치되지 않았습니다."
    echo ""
    echo "의존성 설치 중..."
    pip install -q -r tests/requirements.txt
    echo "✓ 의존성 설치 완료"
else
    echo "✓ Python 의존성 확인 완료"
fi
echo ""

# 테스트 실행
echo "4. S3 버킷 구성 테스트 실행..."
echo "=========================================="
python3 -m pytest tests/test_s3_bucket_config.py -v

echo ""
echo "=========================================="
echo "✓ 모든 테스트 완료!"
echo "=========================================="
