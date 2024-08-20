from pydantic import BaseModel
from src.getinfo.rpatools import nvd
from src.getinfo.preprocessing import normalize_cve_format

class InfoServiceError(Exception):
    pass

class CVERequest(BaseModel):  # CVERequest 모델 추가
    cve_code: str


def get_info(cve_code: str):
    try:
        # CVE 코드 정규화
        normalized_code = normalize_cve_format(cve_code)
        
        # CVE 정보 가져오기
        info_result = nvd(normalized_code)
        
        # CVE 정보가 없는 경우 처리
        if not info_result:
            raise InfoServiceError("CVE 정보를 찾을 수 없습니다.")
        
        return info_result
    
    except InfoServiceError as e:
        # 사용자 정의 예외 처리
        raise e
    except Exception as e:
        # 기타 예외 처리
        raise InfoServiceError(str(e))
