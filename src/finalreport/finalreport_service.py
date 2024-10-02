from src.database.supabase_client import get_supabase_client
from src.auth.auth_service import getuserinfo
from src.database.comment_data import *
from src.openai.openai_service import generate_report
from fastapi import Request, Response
from fastapi.responses import RedirectResponse

supabase = get_supabase_client()

async def get_final_create(request: Request, response: Response, infoid: str, testid: str, client, ):
      # 사용자 정보 가져오기
    user_info = getuserinfo(client=client, response=response, request=request)
    if isinstance(user_info, RedirectResponse):
        return user_info
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
    
    # 보고서 생성
    report_content = await generate_report(info_result.data, test_result.data)

    # 최종 보고서를 DB에 저장
    report_data = {
        "user_id": user_id,
        "info_id": infoid,
        "test_id": testid,
        "content": report_content,
        "cve": info_result.data[0].get('cve')
    }
    
    response = supabase.table("final_report").insert(report_data).execute()

    if not response.data:
        raise Exception("최종 보고서 저장에 실패했습니다.")
    
    report_id = response.data[0]['id']  # 보고서 ID 가져오기
    return report_id, report_content

async def get_final_info(request: Request, response: Response, infoid: str, testid: str, report_id, client):
    # 사용자 정보 가져오기
    user_info = getuserinfo(client=client,response=response,request=request)
    if isinstance(user_info, RedirectResponse):
        return user_info
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
    
     # Supabase에서 최종보고서 가져오기
    final_result = supabase \
        .from_("final_report") \
        .select("*") \
        .eq("id", report_id) \
        .eq("user_id", user_id) \
        .execute()
    
    info_data = info_result.data[0] if info_result.data else None
    test_data = test_result.data[0] if test_result.data else None
    final_data = final_result.data[0] if  final_result.data else None

    return {
            "info": info_data,
            "test": test_data,
            "final": final_data
        }

async def get_final_info_ids(request: Request, response: Response, report_id:str, client):
    # 사용자 정보 가져오기
    user_info = getuserinfo(client=client,response=response,request=request)
    if isinstance(user_info, RedirectResponse):
        return user_info
    user_id = user_info["user"].user.id

    # Supabase에서 최종보고서의 infoid , testid, 가져오기
    final_ids = supabase \
        .from_("final_report") \
        .select("info_id, test_id") \
        .eq("id", report_id) \
        .eq("user_id", user_id) \
        .execute()
    
    # Supabase에서 최종보고서 의 comments 가져오기
    comments = supabase \
        .from_("comments") \
        .select("*") \
        .eq("report_id", report_id) \
        .eq("user_id", user_id) \
        .execute()
        
    # Supabase에서 최종보고서의 모든 코멘트 가져오기
    comments = supabase \
    .from_("comments") \
    .select("*") \
    .eq("report_id", report_id) \
    .eq("user_id", user_id) \
    .execute()
    
    # 코멘트 데이터가 없다면 빈 리스트로 처리
    comments_data = comments.data if comments.data else []

    final_data = final_ids.data[0]

    return {
        "infoid": final_data["info_id"],
        "testid": final_data["test_id"],
        "comments": comments_data
    }

async def add_comment(request: Request, comment: Comment, response: Response, client) -> Comment:
    # 사용자 정보 가져오기
    user_info = getuserinfo(client=client, response=response, request=request)
    if isinstance(user_info, RedirectResponse):
        return user_info
    
    user_id = user_info["user"].user.id

    # 사용자 ID를 comment 객체에 추가
    comment_data = comment.model_dump()
    comment_data['user_id'] = user_id

    print(f"Comment data to be inserted: {comment_data}")

    # Supabase에 코멘트 데이터 추가
    response_data = client.table("comments").insert(comment_data).execute()

    # 응답의 data 속성 확인
    if not response_data.data:
        raise Exception("Failed to add comment: No data returned")

    print(f"Response data: {response_data.data}")

    return Comment(**response_data.data[0])


    
    

