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
    snort_community_rule: dict = None
    emerging_rule: dict = None
    poc: dict = None
    reference: dict = None
    cve: str = None
    last_modified_date: str = None  
    cve_posting_date: str = None 
    user_id: str = None
    attack_vector: str = None
    attack_complexity: str = None
    privileges_required: str = None
    user_interaction: str = None
    scope: str = None
    confidentiality_impact: str = None
    integrity_impact: str = None
    availability_impact: str = None