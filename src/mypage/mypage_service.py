from supabase import Client
from fastapi import HTTPException, Response, Request
from src.auth.auth_service import *

def chage_gpt(response:Response,client: Client, request:Request,key):
    try:
        user_info = getuserinfo(client=client,response=response,request=request)
        user_id = user_info["user"].user.id
        user = client.table("userinfo").update({"account": key}).eq("id", user_id).execute()
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def chage_card(response:Response,client: Client, request:Request,key):
    try:
        user_info = getuserinfo(client=client,response=response,request=request)
        user_id = user_info["user"].user.id
        user = client.table("userinfo").update({"card": key}).eq("id", user_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def past_test(response:Response,client: Client, request:Request):
    try:
        user_info = getuserinfo(client=client,response=response,request=request)
        user_id = user_info["user"].user.id
        past_test = client.table("test_result").select("*").eq("user_id", user_id).execute()
        
        return past_test.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def past_info(response:Response,client: Client, request:Request):
    try:
        user_info = getuserinfo(client=client,response=response,request=request)
        user_id = user_info["user"].user.id
        past_test = client.table("info").select("*").eq("user_id", user_id).execute()
        return past_test.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    
def past_final(response:Response,client: Client,request:Request):
    try:
        user_info = getuserinfo(client=client,response=response,request=request)
        user_id = user_info["user"].user.id
        past_final = client.table("final_report").select("*").eq("user_id", user_id).execute()
        
        return past_final.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

