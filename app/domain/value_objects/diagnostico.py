"""
Value Object: Diagnostico

Agrupa el motivo de consulta y el diagnóstico resultante. Se modela como
Value Object (no como campos sueltos en la entidad) porque ambos datos
viajan siempre juntos y tienen una regla de validación compartida: el
motivo de consulta es obligatorio, el diagnóstico puede quedar pendiente
si la atención aún está en curso (ej. se está esperando un estudio).

`dias_evolucion_sintomas` también vive aquí (no en SignosVitales, que
son mediciones físicas): es parte de la narrativa clínica del
padecimiento — cuánto tiempo lleva el paciente con síntomas antes de
esta consulta — no una medición tomada en el momento.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Diagnostico:
    motivo_consulta: str
    descripcion: str | None = None
    dias_evolucion_sintomas: int | None = None

    def __post_init__(self) -> None:
        if not self.motivo_consulta or not self.motivo_consulta.strip():
            raise ValueError("El motivo de consulta no puede estar vacío.")
        if self.dias_evolucion_sintomas is not None and self.dias_evolucion_sintomas < 0:
            raise ValueError("Los días de evolución de síntomas no pueden ser negativos.")
