"""
Inyección de dependencias del Microservicio de Atención Médica.

Mismo principio que en MS1: este es el único lugar donde se conectan
los puertos (interfaces) con sus implementaciones concretas.
"""
from typing import Annotated

import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.commands.handlers.crear_atencion_handler import CrearAtencionUseCase
from app.application.commands.handlers.modificar_atencion_handler import ModificarAtencionUseCase
from app.application.commands.handlers.sincronizar_atenciones_handler import (
    SincronizarAtencionesBatchUseCase,
)
from app.application.ports.evidencia_storage_port import EvidenciaStoragePort
from app.application.ports.paciente_client_port import PacienteClientPort
from app.application.ports.personal_client_port import PersonalClientPort
from app.application.queries.handlers.listar_atenciones_paciente_handler import (
    ListarAtencionesPorPacienteUseCase,
)
from app.application.queries.handlers.obtener_detalle_atencion_handler import (
    ObtenerDetalleAtencionUseCase,
)
from app.domain.repositories.atencion_command_repository import AtencionCommandRepository
from app.domain.repositories.atencion_query_repository import AtencionQueryRepository
from app.infrastructure.adapters.output.external_services.pacientes_client import PacienteClient
from app.infrastructure.adapters.output.external_services.personal_client import PersonalClient
from app.infrastructure.adapters.output.persistence.atencion_command_repository_impl import (
    AtencionCommandRepositoryImpl,
)
from app.infrastructure.adapters.output.persistence.atencion_query_repository_impl import (
    AtencionQueryRepositoryImpl,
)
from app.infrastructure.adapters.output.storage.cloudinary_storage_adapter import (
    CloudinaryStorageAdapter,
)
from app.infrastructure.config.database import get_db_session
from app.infrastructure.config.settings import get_settings

settings = get_settings()

# Cliente httpx compartido a nivel de módulo: reutiliza el pool de
# conexiones entre requests en vez de abrir una conexión TCP nueva por
# cada llamada a MS1, lo cual sería costoso en alta frecuencia de
# sincronización batch.
_http_client_ms_pacientes = httpx.AsyncClient(
    base_url=settings.ms_pacientes_base_url,
    timeout=settings.ms_pacientes_timeout_seconds,
)


def get_atencion_command_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AtencionCommandRepository:
    return AtencionCommandRepositoryImpl(session)


def get_atencion_query_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AtencionQueryRepository:
    return AtencionQueryRepositoryImpl(session)


def get_paciente_client() -> PacienteClientPort:
    return PacienteClient(_http_client_ms_pacientes)


def get_personal_client() -> PersonalClientPort:
    return PersonalClient(_http_client_ms_pacientes)


def get_evidencia_storage() -> EvidenciaStoragePort:
    return CloudinaryStorageAdapter()


def get_crear_atencion_use_case(
    atencion_repository: Annotated[AtencionCommandRepository, Depends(get_atencion_command_repository)],
    paciente_client: Annotated[PacienteClientPort, Depends(get_paciente_client)],
    personal_client: Annotated[PersonalClientPort, Depends(get_personal_client)],
    evidencia_storage: Annotated[EvidenciaStoragePort, Depends(get_evidencia_storage)],
) -> CrearAtencionUseCase:
    return CrearAtencionUseCase(atencion_repository, paciente_client, personal_client, evidencia_storage)


def get_sincronizar_atenciones_batch_use_case(
    crear_atencion_use_case: Annotated[CrearAtencionUseCase, Depends(get_crear_atencion_use_case)],
) -> SincronizarAtencionesBatchUseCase:
    return SincronizarAtencionesBatchUseCase(crear_atencion_use_case)


def get_modificar_atencion_use_case(
    atencion_repository: Annotated[AtencionCommandRepository, Depends(get_atencion_command_repository)],
    evidencia_storage: Annotated[EvidenciaStoragePort, Depends(get_evidencia_storage)],
) -> ModificarAtencionUseCase:
    return ModificarAtencionUseCase(atencion_repository, evidencia_storage)


def get_listar_atenciones_paciente_use_case(
    query_repository: Annotated[AtencionQueryRepository, Depends(get_atencion_query_repository)],
) -> ListarAtencionesPorPacienteUseCase:
    return ListarAtencionesPorPacienteUseCase(query_repository)


def get_obtener_detalle_atencion_use_case(
    query_repository: Annotated[AtencionQueryRepository, Depends(get_atencion_query_repository)],
) -> ObtenerDetalleAtencionUseCase:
    return ObtenerDetalleAtencionUseCase(query_repository)


# TODO: agregar aquí la dependencia de ListarAtencionesPorPersonalUseCase
# una vez implementado su handler (listar_atenciones_personal_handler.py),
# siguiendo exactamente el mismo patrón que
# get_listar_atenciones_paciente_use_case.
