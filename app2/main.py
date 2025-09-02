# app2/main.py

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from config import settings
from utils import session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Patriotic Keys API", debug=settings.DEBUG)
app.state.session_store = session.session_store

# CORS setup
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
origins = [FRONTEND_ORIGIN]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

@app.on_event("startup")
async def startup_event():
    logging.info("🚀 Patriotic Keys API starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("🛑 Patriotic Keys API shutting down")

# Static files first
app.mount("/assets", StaticFiles(directory="static/dist/assets"), name="assets")

# API routes second
app.include_router(router)

# Root path (fallback for frontend) last
@app.get("/")
def serve_root():
    return FileResponse("static/dist/index.html")

# app.mount("/", StaticFiles(directory="static/dist", html=True), name="static-root")

@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    return FileResponse("static/dist/index.html")