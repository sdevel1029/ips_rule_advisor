# src/openai/openai_routes.py
from fastapi import APIRouter, HTTPException
from src.openai.openai_service import generate_text, GPTRequest

router = APIRouter()

@router.post("/generate/")
async def generate_text_route(request: GPTRequest):
    try:
        return generate_text(request)
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
