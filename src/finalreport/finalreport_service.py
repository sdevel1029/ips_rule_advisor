from src.database.supabase_client import get_supabase_client
from src.auth.auth_service import profile  
from src.database.comment_data import *
from fastapi import Request

supabase = get_supabase_client()

def get_final_report(request: Request, cve_code: str):
    # 쿠키에서 사용자 세션을 통해 사용자 정보 가져오기
    user_profile = profile(supabase, request)
    user_id = user_profile['user'].user.id

    # Supabase에서 사용자와 CVE 코드가 일치하는 정보 조회
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
    
    # Supabase에서 댓글 데이터 조회
    comment_result = supabase \
        .from_("comments") \
        .select("*") \
        .eq("cve", cve_code) \
        .execute()

    # Supabase 쿼리 결과에서 실제 데이터 추출
    results = {
        "info": info_result.data,
        "test": test_result.data,
        "comments": comment_result.data if comment_result.data else []
    }
    
    return results

async def add_comment(request: Request, comment: Comment) -> Comment:
    user_profile = profile(supabase, request)
    user_id = user_profile['user'].user.id

    print(user_id)
    # 사용자 ID를 comment 객체에 추가
    comment_data = comment.model_dump()
    comment_data['user_id'] = user_id

    print(f"Comment data to be inserted: {comment_data}")

    response = supabase.table("comments").insert(comment_data).execute()

    # 응답의 data 속성 확인
    if not response.data:
        raise Exception("Failed to add comment: No data returned")

    print(f"Response data: {response.data}")

    return Comment(**response.data[0])