"""
Puerto de salida: PacienteClientPort

Define el contrato que el dominio/aplicación espera para validar
pacientes contra el Microservicio 1, sin saber NADA de cómo se hace esa
llamada (HTTP, gRPC, etc.). La implementación concreta
(pacientes_client.py) usa httpx para hacer la llamada REST real.

El resultado es un Optional explícito en vez de lanzar excepción
directamente, porque "no se pudo contactar" (timeout) y "se contactó
pero no existe" son dos casos MUY distintos en este dominio (ver
EstadoAtencion: PENDIENTE_VALIDACION vs RECHAZADA) y el llamador
necesita poder distinguirlos.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass
class PacienteValidadoDTO:
    id: str
    curp: str
    nombre_completo: str


class PacienteClientPort(ABC):

    @abstractmethod
    async def obtener_paciente(self, paciente_id: UUID) -> PacienteValidadoDTO | None:
        """
        Devuelve None si MS1 confirma que el paciente NO existe (HTTP 404).
        Lanza ServicioExternoNoDisponibleException si MS1 no responde
        (timeout/conexión rechazada) — ese caso se maneja distinto
        (PENDIENTE_VALIDACION), no como "no existe".
        """
        raise NotImplementedError
