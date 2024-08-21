# src/openai/openai_routes.py
from fastapi import APIRouter, HTTPException
from src.openai.openai_service import generate_text

router = APIRouter()

@router.post("/generate/")
async def generate_text_route():
    try:
        return generate_text()
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
