"""
Value Object: Diagnostico

Agrupa el motivo de consulta y el diagnóstico resultante. Se modela como
Value Object (no como campos sueltos en la entidad) porque ambos datos
viajan siempre juntos y tienen una regla de validación compartida: el
motivo de consulta es obligatorio, el diagnóstico puede quedar pendiente
si la atención aún está en curso (ej. se está esperando un estudio).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Diagnostico:
    motivo_consulta: str
    descripcion: str | None = None

    def __post_init__(self) -> None:
        if not self.motivo_consulta or not self.motivo_consulta.strip():
            raise ValueError("El motivo de consulta no puede estar vacío.")
