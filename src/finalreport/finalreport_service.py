from src.database.supabase_client import get_supabase_client
from src.auth.auth_service import profile  
from fastapi import Request

supabase = get_supabase_client()

def get_final_report(request: Request, cve_code: str):
    # 쿠키에서 사용자 세션을 통해 사용자 정보 가져오기
    user_profile = profile(supabase, request)  
    user_id = user_profile['user'].user.id

    # Supabase에서 사용자와 CVE 코드가 일치하는 보고서를 조회
    response = supabase \
        .from_("info") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("cve", cve_code) \
        .execute()

    if response.data and len(response.data) > 0:
        return response.data[0]  # 최종 보고서 데이터 반환
    else:
        return None  # 보고서를 찾을 수 없을 때