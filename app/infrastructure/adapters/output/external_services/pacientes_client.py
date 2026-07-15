"""
Adaptador de salida: PacienteClient

Implementación concreta de PacienteClientPort usando httpx para llamar
al Microservicio 1 vía REST real: GET /pacientes/{id}.

Maneja explícitamente la distinción clave del diseño:
- HTTP 404 (MS1 respondió, paciente no existe) -> devuelve None
- Timeout / conexión rechazada / 5xx -> lanza
  ServicioExternoNoDisponibleException (MS1 "no disponible", no que el
  paciente no exista)

Esta distinción es la que permite que CrearAtencionUseCase decida entre
RECHAZADA y PENDIENTE_VALIDACION correctamente.
"""
from uuid import UUID

import httpx

from app.application.ports.exceptions import ServicioExternoNoDisponibleException
from app.application.ports.paciente_client_port import PacienteClientPort, PacienteValidadoDTO
from app.infrastructure.config.settings import get_settings

settings = get_settings()


class PacienteClient(PacienteClientPort):

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        # Permite inyectar un cliente httpx compartido (ej. desde
        # dependency_injection.py con un pool de conexiones reutilizable),
        # o crear uno nuevo si no se provee (útil en tests).
        self._http_client = http_client or httpx.AsyncClient(
            base_url=settings.ms_pacientes_base_url,
            timeout=settings.ms_pacientes_timeout_seconds,
        )

    async def obtener_paciente(self, paciente_id: UUID) -> PacienteValidadoDTO | None:
        try:
            respuesta = await self._http_client.get(f"/pacientes/{paciente_id}")
        except (httpx.ConnectError, httpx.TimeoutException) as error:
            raise ServicioExternoNoDisponibleException(
                servicio="Microservicio de Pacientes", detalle=str(error)
            ) from error

        if respuesta.status_code == 404:
            return None

        if respuesta.status_code >= 500:
            raise ServicioExternoNoDisponibleException(
                servicio="Microservicio de Pacientes",
                detalle=f"HTTP {respuesta.status_code}",
            )

        respuesta.raise_for_status()
        data = respuesta.json()
        return PacienteValidadoDTO(
            id=data["id"],
            curp=data["curp"],
            nombre_completo=data["nombre_completo"],
        )
