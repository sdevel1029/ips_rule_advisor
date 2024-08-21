from fastapi import APIRouter
from src.getinfo.getinfo_service import get_info, CVERequest

router = APIRouter()

@router.post("/getinfo")
def get_info_route(request: CVERequest):
    return get_info(request.cve_code)