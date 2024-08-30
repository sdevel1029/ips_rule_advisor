# src/database/supabase_client.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase URL과 키 설정
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    return create_client(url, key)
