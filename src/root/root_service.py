from supabase import Client
from fastapi import HTTPException, Request

def get_past_cve_list(client: Client, request: Request):
    # 쿠키에서 사용자 정보 가져오기
    user = request.cookies.get("user")
    
    # 사용자 정보 가져오기 
    user_info = client.auth.get_user(user)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user_info.user.id
    
    # 해당 사용자의 정보 수집(CVE) 리스트 가져오기
    response = client.table("info").select("cve").eq("user_id", user_id).execute()
    
    # 데이터가 없는 경우에 대한 처리
    if not response.data:
        return []
    
    return response.data