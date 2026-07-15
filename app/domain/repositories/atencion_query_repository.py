"""
Puerto de salida: AtencionQueryRepository

Lado de LECTURA de CQRS. Optimizado para consultas, sin necesidad de
cargar el agregado completo con todas sus reglas de negocio — puede
devolver directamente DTOs/proyecciones en vez de entidades de dominio
completas, si la implementación concreta lo decide así (ver TODO en
atencion_query_repository_impl.py).
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.atencion import Atencion


class AtencionQueryRepository(ABC):

    @abstractmethod
    async def listar_por_paciente(self, paciente_id: UUID) -> list[Atencion]:
        """Historial de atenciones de un paciente específico, sin importar quién lo atendió."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_personal(self, personal_id: UUID) -> list[Atencion]:
        """Atenciones realizadas por un médico/enfermera específico."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_detalle(self, atencion_id: UUID) -> Atencion | None:
        """Detalle completo de una atención, incluyendo medicamentos y evidencia."""
        raise NotImplementedError
