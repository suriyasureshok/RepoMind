# api/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.routes import router
from core.logging import logger
from core.utils import RepoMindError, shutdown_manager
from queue_system import RedisClient


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        yield
    finally:
        shutdown_manager.request_shutdown("fastapi-lifespan-shutdown")
        await RedisClient.close_client()


app = FastAPI(title="RepoMind API", lifespan=lifespan)


@app.exception_handler(RepoMindError)
async def repomind_error_handler(_request: Request, exc: RepoMindError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(Exception)
async def unhandled_error_handler(_request: Request, exc: Exception):
    logger.error(f"Unhandled API exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(router)
