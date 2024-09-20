from supabase import Client
from fastapi import HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel

def chage_gpt(client: Client, request:Request,key):
    try:
        user = request.cookies.get("user")
        user_info = client.auth.get_user(user)
        user_id = user_info.user.id
        user = client.table("userinfo").update({"account": key}).eq("id", user_id).execute()
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def chage_card(client: Client, request:Request,key):
    try:
        user = request.cookies.get("user")
        user_info = client.auth.get_user(user)
        user_id = user_info.user.id
        user = client.table("userinfo").update({"card": key}).eq("id", user_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def past_test(client: Client, request:Request):
    try:
        user = request.cookies.get("user")
        user_info = client.auth.get_user(user)
        user_id = user_info.user.id
        past_test = client.table("test_result").select("*").eq("user_id", user_id).execute()
        
        return past_test.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def past_info(client: Client, request:Request):
    try:
        user = request.cookies.get("user")
        user_info = client.auth.get_user(user)
        user_id = user_info.user.id
        past_test = client.table("info").select("*").eq("user_id", user_id).execute()
        return past_test.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    
def past_final(client: Client,request:Request):
    try:
        user = request.cookies.get("user")
        user_info = client.auth.get_user(user)
        user_id = user_info.user.id
        past_final = client.table("final_report").select("*").eq("user_id", user_id).execute()
        
        return past_final.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
