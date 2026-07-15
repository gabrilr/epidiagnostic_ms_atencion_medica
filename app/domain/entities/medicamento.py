"""
Entidad: Medicamento

Entidad interna del agregado Atencion. Representa un medicamento
recetado dentro de una atención médica específica.
"""
import uuid
from dataclasses import dataclass, field


@dataclass
class Medicamento:
    nombre: str
    dosis: str
    frecuencia: str
    duracion: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del medicamento no puede estar vacío.")
