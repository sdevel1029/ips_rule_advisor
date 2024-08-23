# src/openai/openai_routes.py
from fastapi import APIRouter, HTTPException, Request
from src.openai.openai_service import generate_text, chat_with_gpt


router = APIRouter()

@router.post("/generate/")
async def generate_text_route():
    try:
        return generate_text()
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    chat_message = data.get("message", "")
    reply = await chat_with_gpt(chat_message)
    return reply