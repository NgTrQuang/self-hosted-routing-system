import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import route, places, history
from app.config import ALLOWED_ORIGINS
from app.db.base import init_db
import app.db.models  # noqa: F401 — ensure models are registered before create_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Self-Hosted Routing System",
    description="Production-ready routing API backed by OSRM and OpenStreetMap data for Vietnam.",
    version="1.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(route.router, prefix="/api", tags=["Routing"])
app.include_router(places.router, prefix="/api/places", tags=["Places"])
app.include_router(history.router, prefix="/api/history", tags=["History"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
