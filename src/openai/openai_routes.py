# src/openai/openai_routes.py
from fastapi import APIRouter, HTTPException, Request
from src.openai.openai_chat import chat_with_gpt
import uuid

router = APIRouter()

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    chat_message = data.get("message", "")
    cve_code = data.get("cve_code", "")
    session_id = data.get("session_id")
    
    # 세션 ID가 제공되지 않은 경우에만 새로 생성
    if not session_id:
        session_id = str(uuid.uuid4())
        
    reply = await chat_with_gpt(chat_message, session_id, cve_code)
    return {"session_id": session_id, "reply": reply}