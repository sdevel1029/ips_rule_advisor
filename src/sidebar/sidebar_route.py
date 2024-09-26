from fastapi import APIRouter, Request, Depends
from src.database.supabase_client import get_supabase_client
from src.sidebar.sidebar_service import get_past_cve_list

router = APIRouter()

@router.get("/past_info")
async def get_past_info(request: Request, client=Depends(get_supabase_client)):
    past_cve_list = await get_past_cve_list(client, request)  # client, request 순서 맞추기
    return {"past_cve_list": past_cve_list}
