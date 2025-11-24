import logging

from fastapi import APIRouter
from fastapi import Request
from fastapi import WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.ws_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
async def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.websocket("/dashboard/events")
async def dashboard_ws(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        logger.error(f"Dashboard Events WebSocker Error: {e}")
        ws_manager.disconnect(websocket)
