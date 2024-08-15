# src/main.py
from fastapi import FastAPI
from src.auth.auth_routes import router as auth_router
from src.openai.openai_routes import router as openai_router
import uvicorn

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(openai_router, prefix="/openai", tags=["openai"])

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)