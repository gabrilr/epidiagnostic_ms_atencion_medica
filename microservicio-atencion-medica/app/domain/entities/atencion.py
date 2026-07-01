"""
Entidad raíz de agregado: Atencion

Es la raíz del agregado Atencion, que también incluye Medicamento (lista)
y EvidenciaReceta (opcional) como entidades internas.

No duplica datos de Paciente ni de PersonalMedico — solo guarda las
referencias externas (paciente_id, personal_id) obtenidas del
Microservicio 1. Por la decisión de diseño confirmada ("atenciones
independientes, sin conflicto"), múltiples atenciones pueden referenciar
al mismo paciente_id sin ningún tipo de coordinación entre ellas.

El campo `estado` es clave para la tolerancia a fallos en la
comunicación con MS1 (ver EstadoAtencion).
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.domain.entities.evidencia_receta import EvidenciaReceta
from app.domain.entities.medicamento import Medicamento
from app.domain.value_objects.diagnostico import Diagnostico
from app.domain.value_objects.estado_atencion import EstadoAtencion


@dataclass
class Atencion:
    paciente_id: uuid.UUID
    personal_id: uuid.UUID
    diagnostico: Diagnostico
    fecha_atencion: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    device_generated_id: str | None = None  # trazabilidad del celular, no es clave de negocio
    estado: EstadoAtencion = EstadoAtencion.REGISTRADA
    medicamentos: list[Medicamento] = field(default_factory=list)
    evidencia_receta: EvidenciaReceta | None = None
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.fecha_atencion > datetime.utcnow():
            raise ValueError("La fecha de atención no puede ser futura.")

    def marcar_validada(self) -> None:
        self.estado = EstadoAtencion.VALIDADA
        self.actualizado_en = datetime.utcnow()

    def marcar_pendiente_validacion(self) -> None:
        """MS1 no respondió (timeout/caído); se revalidará más tarde, no se rechaza la atención."""
        self.estado = EstadoAtencion.PENDIENTE_VALIDACION
        self.actualizado_en = datetime.utcnow()

    def marcar_rechazada(self) -> None:
        """MS1 confirmó que paciente o personal no existen; este sí es un error real."""
        self.estado = EstadoAtencion.RECHAZADA
        self.actualizado_en = datetime.utcnow()

    def agregar_medicamento(self, medicamento: Medicamento) -> None:
        self.medicamentos.append(medicamento)
        self.actualizado_en = datetime.utcnow()

    def adjuntar_evidencia(self, evidencia: EvidenciaReceta) -> None:
        """
        Asigna o reemplaza la evidencia fotográfica de la receta. A
        diferencia del historial médico en MS1 (que es append-only), aquí
        solo puede existir UNA evidencia por atención — si se sube una
        nueva, reemplaza a la anterior (caso de uso: corregir una foto
        borrosa).
        """
        self.evidencia_receta = evidencia
        self.actualizado_en = datetime.utcnow()
