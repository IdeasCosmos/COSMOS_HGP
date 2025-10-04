"""
COSMOS-HGP Authentication Module
API 키 인증 시스템
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security
bearer_scheme = HTTPBearer()
API_KEY = "test_key_12345"

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    API 키 검증 함수
    
    Args:
        credentials: Bearer 토큰 인증 정보
        
    Raises:
        HTTPException: API 키가 유효하지 않을 경우 401 에러
        
    Returns:
        str: 검증된 API 키
    """
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Use 'Bearer' token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return credentials.credentials

