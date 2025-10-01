"""
COSMOS Exceptions
커스텀 예외 클래스
"""


class ProFeatureError(Exception):
    """
    Pro 기능 사용 시 발생하는 예외
    
    무료 버전에서 Pro 기능을 호출하거나
    API 키가 유효하지 않을 때 발생
    """
    
    def __init__(self, message="This feature requires COSMOS Pro subscription"):
        self.message = message
        super().__init__(self.message)


class CosmosEngineError(Exception):
    """
    엔진 실행 중 발생하는 예외
    """
    
    def __init__(self, message="Engine execution failed"):
        self.message = message
        super().__init__(self.message)


class InvalidDataError(Exception):
    """
    잘못된 데이터 입력 시 발생하는 예외
    """
    
    def __init__(self, message="Invalid data format"):
        self.message = message
        super().__init__(self.message)


class APIConnectionError(Exception):
    """
    API 연결 실패 시 발생하는 예외
    """
    
    def __init__(self, message="Failed to connect to COSMOS API"):
        self.message = message
        super().__init__(self.message)


class QuotaExceededError(Exception):
    """
    API 호출 할당량 초과 시 발생하는 예외
    """
    
    def __init__(self, message="API quota exceeded"):
        self.message = message
        super().__init__(self.message)
