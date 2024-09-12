from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

app = FastAPI()

# Supabase 클라이언트 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 데이터 모델 정의
class VulnerabilityCreate(BaseModel):
    vuln_type: str
    description: str
    cpe: dict = None
    metric: str = None
    score: float = None
    influence_score: float = None
    exploit_score: float = None
    metrics_summary: str
    related_rules_type: dict = None
    related_rules_product: dict = None
    poc: dict = None
    reference: dict = None
    cve: str = None
    last_modified_date: str = None  
    cve_posting_date: str = None 
    user_id: str = None