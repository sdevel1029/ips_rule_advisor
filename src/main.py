from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.auth.auth_routes import router as auth_router
from src.openai.openai_routes import router as openai_router
from src.root.root import router as root_router
from src.getinfo.getinfo_routes import router as getinfo_router
import uvicorn

app = FastAPI()

# Static files setup
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Include routers
app.include_router(auth_router, prefix="/auth")
app.include_router(openai_router, prefix="/openai", tags=["openai"])
app.include_router(root_router)  
app.include_router(getinfo_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
