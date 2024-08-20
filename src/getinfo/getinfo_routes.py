from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.getinfo.getinfo_service import nvd 
from src.getinfo.preprocessing import normalize_cve_format

router = APIRouter()

class CVERequest(BaseModel):
    cve_code: str

@router.post("/getinfo")
def get_info_route(request: CVERequest):
    code = request.cve_code
    if not code:
        raise HTTPException(status_code=400, detail="CVE 코드가 필요합니다.")
    
    try:
        info = nvd(code)
        if not info:
            raise HTTPException(status_code=404, detail="CVE 정보를 찾을 수 없습니다.")
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cve/{cve_code}")
async def get_cve_info(cve_code: str):
    try:
        # CVE 코드 정규화
        normalized_code = normalize_cve_format(cve_code)
        
        # CVE 정보 가져오기
        info_result = nvd(normalized_code)
        
        # 결과 반환
        return {"cve_code": normalized_code, "info": info_result}
    except Exception as e:
        # 오류 처리
        raise HTTPException(status_code=400, detail=str(e))