from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")

@router.get("/ruletest", response_class=HTMLResponse)
async def ruletest(request: Request):
    return templates.TemplateResponse("ruletest.html", {"request": request})
