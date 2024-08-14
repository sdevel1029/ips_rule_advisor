# src/openai/openai_service.py
import openai
from pydantic import BaseModel
from fastapi import HTTPException
from dotenv import load_dotenv
import os

#환경변수를 불러오는 변수입니다
load_dotenv()

#openai api key입니다
openai.api_key = os.getenv("OPENAI_API_KEY")


class GPTRequest(BaseModel):
    prompt: str
    max_tokens: int = 100

def generate_text(request: GPTRequest):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # 모델 이름은 사용 가능한 모델로 변경 가능
            prompt=request.prompt,
            max_tokens=request.max_tokens
        )
        return {"response": response.choices[0].text.strip()}
        except openai.error.OpenAIError as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
