# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SUPABASE_URL: str = os.getenv("https://hjneilihqnqaekpwkpkx.supabase.co")
    SUPABASE_KEY: str = os.getenv(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhqbmVpbGlocW5xYWVrcHdrcGt4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjA2OTQ0OTIsImV4cCI6MjAzNjI3MDQ5Mn0.yv3BRlAP53X8VrIwNs1CYWeEKVCLBKfIn797dEbsM2M"
    )
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")


settings = Settings()
