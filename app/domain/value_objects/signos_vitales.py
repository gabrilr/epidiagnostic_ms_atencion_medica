"""
Value Object: SignosVitales

Mediciones físicas tomadas durante una atención puntual (no datos
duraderos del paciente, por eso viven aquí y no en el historial médico
del Microservicio 1). Todos los campos son opcionales porque, en
consultas rurales, no siempre se dispone del equipo para medir todos
(ej. no siempre hay glucómetro u oxímetro a la mano) — se captura lo que
se pueda, nunca se obliga a inventar un valor.

Los rangos de validación son fisiológicos amplios (no clínicos
estrictos): solo buscan atrapar errores de captura evidentes (ej. un
"999" en temperatura), no sustituir el criterio médico.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SignosVitales:
    presion_sistolica: int | None = None
    presion_diastolica: int | None = None
    temperatura: float | None = None
    peso: float | None = None
    estatura: float | None = None
    glucosa: float | None = None
    frecuencia_cardiaca: int | None = None
    saturacion_oxigeno: int | None = None

    def __post_init__(self) -> None:
        if self.presion_sistolica is not None and not (60 <= self.presion_sistolica <= 260):
            raise ValueError("La presión sistólica debe estar entre 60 y 260 mmHg.")
        if self.presion_diastolica is not None and not (30 <= self.presion_diastolica <= 150):
            raise ValueError("La presión diastólica debe estar entre 30 y 150 mmHg.")
        if self.temperatura is not None and not (30.0 <= self.temperatura <= 45.0):
            raise ValueError("La temperatura debe estar entre 30 y 45 °C.")
        if self.peso is not None and not (1 <= self.peso <= 300):
            raise ValueError("El peso debe estar entre 1 y 300 kg.")
        if self.estatura is not None and not (30 <= self.estatura <= 250):
            raise ValueError("La estatura debe estar entre 30 y 250 cm.")
        if self.glucosa is not None and not (20 <= self.glucosa <= 600):
            raise ValueError("La glucosa debe estar entre 20 y 600 mg/dL.")
        if self.frecuencia_cardiaca is not None and not (30 <= self.frecuencia_cardiaca <= 220):
            raise ValueError("La frecuencia cardíaca debe estar entre 30 y 220 lpm.")
        if self.saturacion_oxigeno is not None and not (0 <= self.saturacion_oxigeno <= 100):
            raise ValueError("La saturación de oxígeno debe estar entre 0 y 100%.")
