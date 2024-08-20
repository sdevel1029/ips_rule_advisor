from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from src.getinfo.getinfo_service import nvd 
from src.getinfo.preprocessing import normalize_cve_format
import os

router = APIRouter()

class CVERequest(BaseModel):
    cve_code: str

@router.post("/getinfo")
async def get_info_route(request: CVERequest):  # JSON 데이터를 받음
    cve_code = request.cve_code
    if not cve_code:
        raise HTTPException(status_code=400, detail="CVE 코드가 필요합니다.")
    
    try:
        # CVE 코드 정규화 및 정보 조회
        normalized_code = normalize_cve_format(cve_code)
        info = nvd(normalized_code)
        
        if not info:
            raise HTTPException(status_code=404, detail="CVE 정보를 찾을 수 없습니다.")
        
        # 결과 데이터를 JSON으로 반환
        return JSONResponse(content={"cve_code": normalized_code, "info": info})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

