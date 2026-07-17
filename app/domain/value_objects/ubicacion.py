"""
Value Object: Ubicacion

Dónde se realizó una atención médica (ej. "Suchiapa"), no necesariamente
la misma ubicación que la residencia del paciente ni la asignación
habitual del personal médico — las brigadas itinerantes en comunidades
rurales de Chiapas suelen atender en una comunidad distinta a ambas.

Duplicado deliberadamente del VO homónimo en el Microservicio 1: ambos
microservicios son despliegues independientes (database per service, sin
shared kernel), así que no importan código de dominio entre sí.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Ubicacion:
    comunidad: str
    municipio: str

    def __post_init__(self) -> None:
        if not self.comunidad or not self.comunidad.strip():
            raise ValueError("La comunidad no puede estar vacía.")
        if not self.municipio or not self.municipio.strip():
            raise ValueError("El municipio no puede estar vacío.")

    def __str__(self) -> str:
        return f"{self.comunidad}, {self.municipio}"
