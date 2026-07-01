"""
Puerto de salida: AtencionCommandRepository

Lado de ESCRITURA de CQRS. Define el contrato para persistir y
modificar atenciones. Separado deliberadamente de
AtencionQueryRepository (lado de lectura) aunque ambos puedan
implementarse contra la misma base de datos física — la separación es
a nivel de aplicación/dominio, no necesariamente de infraestructura
(ver discusión de diseño sobre CQRS sin necesidad de dos bases físicas).
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.atencion import Atencion


class AtencionCommandRepository(ABC):

    @abstractmethod
    async def guardar(self, atencion: Atencion) -> Atencion:
        """Persiste una atención nueva."""
        raise NotImplementedError

    @abstractmethod
    async def buscar_por_id(self, atencion_id: UUID) -> Atencion | None:
        """
        Necesario también en el lado de comandos (no solo en queries)
        porque ModificarAtencionUseCase necesita cargar la entidad antes
        de mutarla y volver a guardarla.
        """
        raise NotImplementedError

    @abstractmethod
    async def buscar_por_device_generated_id(self, device_generated_id: str) -> Atencion | None:
        """
        Soporta la idempotencia del batch de sincronización: si el
        celular reintenta el mismo batch (porque no supo si la primera
        vez tuvo éxito), este método permite detectar que esa atención
        ya fue procesada y evitar duplicarla.
        """
        raise NotImplementedError

    @abstractmethod
    async def actualizar(self, atencion: Atencion) -> Atencion:
        """Persiste cambios sobre una atención existente."""
        raise NotImplementedError
