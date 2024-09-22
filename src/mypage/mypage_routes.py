from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.mypage.mypage_service import *
from src.database.supabase_client import get_supabase_client
from src.auth.auth_service import profile
from src.database.info_save import *
from datetime import datetime

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")


@router.get("/mypage", response_class=HTMLResponse)
async def home(request: Request):
    # 사용자 ID(=세션) 가져오기
    user_info = profile(supabase, request)
    if not user_info:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user_id = user_info['user'].user.id 
    
    # 정보 수집 결과라면
    # if info_id:
        # response = supabase.table("info").select("*").eq("id", info_id).execute()
        # raw_data = response.data[0]
        
        # info_result = {}
        # nvd = {}
        # nvd["id"] = raw_data["cve"]
        # nvd["수정시간"] = raw_data["cve_posting_date"]

        # attack_type = raw_data["vuln_type"]

        # attack_description = raw_data["description"]

        # current_date = raw_data["last_modified_date"]

        # return templates.TemplateResponse("info.html",{
        #         "request": request,
        #         "info": info_result,
        #         "type": attack_type,
        #         "type_description" : attack_description,
        #         "metrics_summary": metrics_summary,
        #         "current_date": current_date,
        #         "snort_community_rule": snort_community_rules,
        #         "emerging_rule": emerging_rules
        #         })
        # return {"hello": "world"}

    # 정보수집 기록을 "info_cve"에 넣기. 날짜, cve 만
    response = supabase.table("info").select("last_modified_date, cve, id").eq("user_id", user_id).execute()
    info_cve = []
    for i in response.data:
        tmp_list = []
        tmp_list.append(i["last_modified_date"])
        tmp_list.append(i["cve"])
        tmp_list.append(i["id"])
        info_cve.append(tmp_list)
    info_cve.reverse() # 뒤집어서 최신순으로 만들어주기

    # 테스트 기록을 "test_cve"에 넣기. 날짜, cve, rule 만
    response_test = supabase.table("test_all").select("created_at, cve, rule, id").eq("user_id", user_id).execute()
    test_cve = []
    for i in response_test.data:
        tmp_list = []
        dt = datetime.fromisoformat(i["created_at"])
        date_only = dt.date()
        tmp_list.append(date_only)
        tmp_list.append(i["cve"])
        tmp_list.append(i["rule"])
        tmp_list.append(i["id"])
        test_cve.append(tmp_list)
    test_cve.reverse() # 뒤집어서 최신순으로 만들어주기

    finalreport_test = supabase.table("final_report").select("*").eq("user_id", user_id).execute()
    final = []
    for i in finalreport_test.data:
        tmp_list = []
        dt = datetime.fromisoformat(i["created_at"])
        date_only = dt.date()
        tmp_list.append(date_only)
        tmp_list.append(i["cve"])
        final.append(tmp_list)
    final.reverse() # 뒤집어서 최신순으로 만들어주기

    return templates.TemplateResponse("my_info.html", {"request": request, "info_cve": info_cve, "test_cve": test_cve, "final": final})



@router.get("/gptkey", response_class=HTMLResponse)
async def gpt_key(request: Request):
    return templates.TemplateResponse("chage_gptkey.html", {"request": request})

@router.get("/myaccount", response_class=HTMLResponse)
async def gpt_key(request: Request):
    return templates.TemplateResponse("my_payment.html", {"request": request})

@router.get("/pastresult", response_class=HTMLResponse)
async def past(request: Request,client=Depends(get_supabase_client)):
    final = past_final(client=client,request=request)
    return templates.TemplateResponse("past_result.html", {"data": final,"request": request})

@router.get("/ruleresult", response_class=HTMLResponse)
async def past(request: Request,client=Depends(get_supabase_client)):
    test = past_test(client=client,request=request)
    return templates.TemplateResponse("my_ruletest.html", {"data" : test,"request": request})

@router.get("/ruleshow", response_class=HTMLResponse)
async def past(request: Request,testid,client=Depends(get_supabase_client)):
    test_result = client.table("test_result").select("*").eq("id", testid).execute()
    return templates.TemplateResponse("my_ruletest_show.html", {"test_result": test_result.data[0],"request": request})

@router.get("/info", response_class=HTMLResponse)
async def past(request: Request,client=Depends(get_supabase_client)):
    info = past_info(client=client,request=request)
    return templates.TemplateResponse("my_info_2.html", {"data" : info,"request": request})

@router.get("/infoshow", response_class=HTMLResponse)
async def past(request: Request,uuid,client=Depends(get_supabase_client)):
    info_result = client.table("info").select("*").eq("id", uuid).execute()
    return templates.TemplateResponse("my_info_show.html", {"info" : info_result.data[0],"request": request})


@router.post("/gptkey/change")
async def gpt_key(request: Request,client=Depends(get_supabase_client)):
    data = await request.json()
    key =data.get("key")
    chage_gpt(client=client,request=request,key=key)
    return "success"

@router.post("/card/change")
async def gpt_card(request: Request,client=Depends(get_supabase_client)):
    data = await request.json()
    key =data.get("card")
    chage_card(client=client,request=request,key=key)
    return "success"
