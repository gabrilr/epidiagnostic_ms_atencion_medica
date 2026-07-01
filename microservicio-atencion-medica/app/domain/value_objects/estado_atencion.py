"""
Value Object / Enum: EstadoAtencion

Modela el estado de validación de una atención respecto al Microservicio 1
(Pacientes y Personal), no el estado clínico de la consulta en sí.

Esta máquina de estados existe por la decisión de diseño de tolerancia a
fallos: si el MS1 no responde al validar paciente_id/personal_id, la
atención NO se bloquea — se acepta igual y queda pendiente de validación
para revalidarse después.
"""
from enum import Enum


class EstadoAtencion(str, Enum):
    REGISTRADA = "registrada"                      # recién llegó, aún no se valida contra MS1
    VALIDADA = "validada"                           # MS1 confirmó que paciente y personal existen
    PENDIENTE_VALIDACION = "pendiente_validacion"   # MS1 no respondió (timeout/caído), se revalida después
    RECHAZADA = "rechazada"                         # MS1 respondió pero paciente o personal no existen
