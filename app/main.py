import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api_client import api_client
from app.routes.document import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Arrancando API Integracion AUCO (FastApi)")
    yield
    logger.info("Apagando API Integracion AUCO")
    await api_client.close()
    
    

app = FastAPI(
    title="API Integracion AUCO",
    description="Middleware de integracion entre AUCO y sistema destino (salesforce)",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="app/static"),name="static")


app.include_router(router)

@app.exception_handler(404)
async def not_found(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={"sucess": False, "error": "Recurso no encontrado"}
    )

@app.exception_handler(500)
async def internal_error(request: Request, exc: Exception):
    logger.exception("Error interno del servidor")
    return JSONResponse(
        status_code=500,
        content={"sucess": False, "error": "Error interno del servidor"},
    )
    
    
