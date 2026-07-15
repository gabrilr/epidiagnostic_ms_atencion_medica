"""
Punto de entrada de la aplicación FastAPI del Microservicio de Atención
Médica. Igual de delgado que en MS1: arma la app, registra routers
(comandos y queries, separados por CQRS), y expone health check.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.adapters.input.api.atencion_command_router import (
    router as atencion_command_router,
)
from app.infrastructure.adapters.input.api.atencion_query_router import (
    router as atencion_query_router,
)
from app.infrastructure.config.database import engine
from app.infrastructure.config.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.connect() as connection:
        pass
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description=(
        "Microservicio de gestión de atención médica para "
        "EpiDiagnostic-Maya. Responsable de crear y modificar "
        "atenciones, registro de medicamentos asignados, y evidencia "
        "fotográfica de recetas. Patrón: CQRS (comandos y consultas "
        "separados a nivel de aplicación)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(atencion_command_router)
app.include_router(atencion_query_router)

# TODO: una vez implementados los TODOs pendientes (modificar atención,
# listar por personal), ya quedan incluidos automáticamente porque se
# agregan directamente a los routers ya registrados arriba — no
# requieren un nuevo app.include_router().


@app.get("/health", tags=["Sistema"], summary="Health check para orquestadores/API Gateway")
async def health_check() -> dict:
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}
