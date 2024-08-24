# src/database/supabase_client.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase URL과 키 설정
url= "https://hjneilihqnqaekpwkpkx.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhqbmVpbGlocW5xYWVrcHdrcGt4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjA2OTQ0OTIsImV4cCI6MjAzNjI3MDQ5Mn0.yv3BRlAP53X8VrIwNs1CYWeEKVCLBKfIn797dEbsM2M"

def get_supabase_client() -> Client:
    return create_client(url, key)
