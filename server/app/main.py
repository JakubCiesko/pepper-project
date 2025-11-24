from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import dashboard
from app.routes import detect

app = FastAPI(title="Pepper Object Detection Server", version="0.1.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(detect.router, prefix="/api")
app.include_router(dashboard.router)
