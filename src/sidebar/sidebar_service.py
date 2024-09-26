from supabase import Client
from fastapi import HTTPException, Request

async def get_past_cve_list(client: Client, request: Request):
    # 쿠키에서 사용자 정보 가져오기
    user = request.cookies.get("user")
    
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    # 사용자 정보 가져오기 
    user_info = client.auth.get_user(user)
    
    # user_info가 None인 경우 에러 처리
    if not user_info or not user_info.user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user_info.user.id
    
    # 해당 사용자의 CVE 리스트 가져오기
    response = client.table("info").select("cve").eq("user_id", user_id).execute()
    
    # 데이터가 없는 경우에 대한 처리
    if not response.data:
        return []
    
    return response.data

async def get_past_test_list(client: Client, request: Request):
    # 쿠키에서 사용자 정보 가져오기
    user = request.cookies.get("user")
    
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    # 사용자 정보 가져오기 
    user_info = client.auth.get_user(user)
    
    # user_info가 None인 경우 에러 처리
    if not user_info or not user_info.user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user_info.user.id
    
    # 해당 사용자의 테스트 리스트 가져오기
    response = client.table("test_result").select("cve").eq("user_id", user_id).execute()
    
    # 데이터가 없는 경우에 대한 처리
    if not response.data:
        return []
    
    return response.data