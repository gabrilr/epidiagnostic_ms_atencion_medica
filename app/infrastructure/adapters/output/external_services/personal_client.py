"""
Adaptador de salida: PersonalClient

Espejo de PacienteClient, pero para GET /personal/{id} en MS1.

Nota: este endpoint (GET /personal/{id}) está documentado como TODO en
el Microservicio 1 (ver personal_router.py allá) — este cliente ya
queda listo y correcto para cuando se implemente del otro lado; no
requiere cambios en este microservicio cuando eso pase.
"""
from uuid import UUID

import httpx

from app.application.ports.exceptions import ServicioExternoNoDisponibleException
from app.application.ports.personal_client_port import PersonalClientPort, PersonalValidadoDTO
from app.infrastructure.config.settings import get_settings

settings = get_settings()


class PersonalClient(PersonalClientPort):

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self._http_client = http_client or httpx.AsyncClient(
            base_url=settings.ms_pacientes_base_url,
            timeout=settings.ms_pacientes_timeout_seconds,
        )

    async def obtener_personal(self, personal_id: UUID) -> PersonalValidadoDTO | None:
        try:
            respuesta = await self._http_client.get(f"/personal/{personal_id}")
        except (httpx.ConnectError, httpx.TimeoutException) as error:
            raise ServicioExternoNoDisponibleException(
                servicio="Microservicio de Pacientes (Personal)", detalle=str(error)
            ) from error

        if respuesta.status_code == 404:
            return None

        if respuesta.status_code >= 500:
            raise ServicioExternoNoDisponibleException(
                servicio="Microservicio de Pacientes (Personal)",
                detalle=f"HTTP {respuesta.status_code}",
            )

        respuesta.raise_for_status()
        data = respuesta.json()
        return PersonalValidadoDTO(
            id=data["id"],
            nombre_completo=data["nombre_completo"],
            tipo=data["tipo"],
            activo=data["activo"],
        )
