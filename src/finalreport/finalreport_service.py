from src.database.supabase_client import get_supabase_client
from src.auth.auth_service import profile  
from fastapi import Request

supabase = get_supabase_client()

def get_final_report(request: Request, cve_code: str):
    # 쿠키에서 사용자 세션을 통해 사용자 정보 가져오기
    user_profile = profile(supabase, request)  
    user_id = user_profile['user'].user.id

    info_result = supabase \
        .from_("info") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("cve", cve_code) \
        .execute()

    # Supabase에서 사용자와 CVE 코드가 일치하는 테스트 결과 조회
    test_result = supabase \
        .from_("test_result") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("cve", cve_code) \
        .execute()

    # 결과를 결합
    results = {
        "info": info_result.data,
        "test": test_result.data
    }
    return results