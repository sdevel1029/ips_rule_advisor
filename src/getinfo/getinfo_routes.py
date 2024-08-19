from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.getinfo.getinfo_service import nvd 

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