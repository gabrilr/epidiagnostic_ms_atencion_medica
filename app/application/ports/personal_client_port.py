"""
Puerto de salida: PersonalClientPort

Espejo de PacienteClientPort, pero para validar personal médico contra
el Microservicio 1.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass
class PersonalValidadoDTO:
    id: str
    nombre_completo: str
    tipo: str
    activo: bool


class PersonalClientPort(ABC):

    @abstractmethod
    async def obtener_personal(self, personal_id: UUID, bearer_token: str) -> PersonalValidadoDTO | None:
        """
        `bearer_token`: ver docstring de PacienteClientPort.obtener_paciente
        — se reenvía tal cual a MS1 en vez de que MS2 tenga su propia
        identidad de servicio.

        Devuelve None si MS1 confirma que el personal NO existe (HTTP 404).
        Lanza ServicioExternoNoDisponibleException si MS1 no responde.
        Lanza CredencialesInvalidasException si MS1 responde 401.

        Nota: este método devuelve el personal aunque esté inactivo
        (activo=False); es responsabilidad de quien llama (el caso de uso
        CrearAtencion) decidir si una atención registrada por personal
        inactivo se rechaza o no. Mantener esa regla en el caso de uso, no
        en el cliente, da más flexibilidad para ajustarla sin tocar
        infraestructura.
        """
        raise NotImplementedError
