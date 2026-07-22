"""
Adaptador de salida: PersonalClient

Espejo de PacienteClient, pero para GET /personal/{id} en ms-personal
(MS3) — antes de la separación en 4 microservicios, este endpoint vivía
en el mismo servicio que /pacientes/{id}.

Igual que PacienteClient, reenvía el Bearer del personal que originó la
petición a MS2 — ver docstring de pacientes_client.py.
"""
from uuid import UUID

import httpx

from app.application.ports.exceptions import (
    CredencialesInvalidasException,
    ServicioExternoNoDisponibleException,
)
from app.application.ports.personal_client_port import PersonalClientPort, PersonalValidadoDTO
from app.infrastructure.config.settings import get_settings

settings = get_settings()


class PersonalClient(PersonalClientPort):

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self._http_client = http_client or httpx.AsyncClient(
            base_url=settings.ms_personal_base_url,
            timeout=settings.ms_personal_timeout_seconds,
        )

    async def obtener_personal(self, personal_id: UUID, bearer_token: str) -> PersonalValidadoDTO | None:
        try:
            respuesta = await self._http_client.get(
                f"/personal/{personal_id}",
                headers={"Authorization": f"Bearer {bearer_token}"},
            )
        except (httpx.ConnectError, httpx.TimeoutException) as error:
            raise ServicioExternoNoDisponibleException(
                servicio="Microservicio de Personal", detalle=str(error)
            ) from error

        if respuesta.status_code == 401:
            raise CredencialesInvalidasException(servicio="Microservicio de Personal")

        if respuesta.status_code == 404:
            return None

        if respuesta.status_code >= 500:
            raise ServicioExternoNoDisponibleException(
                servicio="Microservicio de Personal",
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
