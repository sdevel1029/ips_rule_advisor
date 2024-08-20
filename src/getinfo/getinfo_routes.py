from fastapi import APIRouter
from pydantic import BaseModel
from src.getinfo.getinfo_service import get_info

router = APIRouter()

class CVERequest(BaseModel):
    cve_code: str

@router.post("/getinfo")
def get_info_route(request: CVERequest):
    return get_info(request.cve_code)