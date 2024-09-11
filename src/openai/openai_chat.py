#src/openai/openai_chat.py
import json
import os
from dotenv import load_dotenv
import httpx
from src.getinfo.getinfo_service import get_info

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# cve 관리 변수
cve_info_cache = {}

# 세션 관리 변수
session_history = {}

async def load_and_cache_cve_info(cve_code: str):
    # cve 정보를 가져옴
    if cve_code not in cve_info_cache:
        cve_info = await get_info(cve_code)  
        cve_info_cache[cve_code] = cve_info 
    return cve_info_cache[cve_code]

def get_session_history(session_id: str):
    # 세션 ID에 해당하는 대화 기록을 가져옴
    return session_history.get(session_id, [])

def update_session_history(session_id: str, role: str, content: str):
    # 세션 기록에 새로운 대화를 추가함
    if session_id not in session_history:
        session_history[session_id] = []
    session_history[session_id].append({"role": role, "content": content})

def clear_session_history(session_id: str):
    # 세션 기록 초기화
    if session_id in session_history:
        del session_history[session_id]

async def chat_with_gpt(chat_message: str, session_id: str, cve_code: str = None) -> dict:
    context_message = "You are an expert in cybersecurity, and you have access to CVE information. Use this information to help answer the user's questions."
    
    if cve_code:
        cve_info = await load_and_cache_cve_info(cve_code)
        context_message += f"\n\nHere is the CVE information:\n{json.dumps(cve_info, ensure_ascii=False, indent=2)}"

    # 세션 내역 가져오기
    session_history = get_session_history(session_id)
    # 사용자 메시지를 세션 내역에 추가
    session_history.append({"role": "user", "content": chat_message})
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [{"role": "system", "content": context_message}] + session_history,
                'max_tokens': 2000,
                'temperature': 0.3
            }
        )
        response_data = response.json()
        reply = response_data['choices'][0]['message']['content'].strip()
        
        # GPT 응답을 세션 내역에 추가
        update_session_history(session_id, "assistant", reply)
        
        return {"reply": reply}