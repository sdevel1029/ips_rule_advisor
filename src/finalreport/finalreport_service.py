from src.database.supabase_client import get_supabase_client
from src.auth.auth_service import getuserinfo
from src.database.comment_data import *
from src.openai.openai_service import generate_report
from fastapi import Request, Response

supabase = get_supabase_client()

async def get_final_report(request: Request, response: Response, infoid: str, testid: str, client, ):
    user_info = getuserinfo(client=client, response=response, request=request)
    user_id = user_info["user"].user.id

    # Supabase에서 정보 수집 결과 가져오기
    info_result = supabase \
        .from_("info") \
        .select("*") \
        .eq("id", infoid) \
        .eq("user_id", user_id) \
        .execute()

    # Supabase에서 테스트 결과 가져오기
    test_result = supabase \
        .from_("test_result") \
        .select("*") \
        .eq("id", testid) \
        .eq("user_id", user_id) \
        .execute()
    
    # OpenAI GPT 보고서 생성 함수 호출
    report_content = await generate_report(info_result.data, test_result.data)
    return report_content


    
    

