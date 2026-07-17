"""
Modelo SQLAlchemy: AtencionModel

Tabla principal de persistencia. Igual que en MS1, este modelo ORM es
distinto de la entidad de dominio Atencion — la traducción ocurre en
los repositorios (atencion_command_repository_impl.py /
atencion_query_repository_impl.py).

Nota sobre CQRS: aunque conceptualmente comandos y queries están
separados a nivel de aplicación, ambos repositorios leen/escriben sobre
ESTA MISMA tabla física (ver discusión de diseño: CQRS sin necesidad de
dos bases de datos separadas en esta escala).
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.config.database import Base
from app.infrastructure.config.types import GUID


class AtencionModel(Base):
    __tablename__ = "atenciones"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    paciente_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False, index=True)
    personal_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False, index=True)
    motivo_consulta: Mapped[str] = mapped_column(String(500), nullable=False)
    diagnostico_descripcion: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    dias_evolucion_sintomas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_atencion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # Dónde se realizó la atención — no necesariamente donde vive el
    # paciente ni donde está asignado el personal (brigadas itinerantes).
    comunidad: Mapped[str] = mapped_column(String(255), nullable=False)
    municipio: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="registrada")
    device_generated_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True, unique=True, index=True
    )

    # Signos vitales: todos opcionales, se captura lo que se pueda medir.
    presion_sistolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    presion_diastolica: Mapped[int | None] = mapped_column(Integer, nullable=True)
    temperatura: Mapped[float | None] = mapped_column(Float, nullable=True)
    peso: Mapped[float | None] = mapped_column(Float, nullable=True)
    estatura: Mapped[float | None] = mapped_column(Float, nullable=True)
    glucosa: Mapped[float | None] = mapped_column(Float, nullable=True)
    frecuencia_cardiaca: Mapped[int | None] = mapped_column(Integer, nullable=True)
    saturacion_oxigeno: Mapped[int | None] = mapped_column(Integer, nullable=True)

    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    medicamentos: Mapped[list["MedicamentoModel"]] = relationship(
        back_populates="atencion", cascade="all, delete-orphan", lazy="selectin"
    )
    evidencia: Mapped["EvidenciaRecetaModel | None"] = relationship(
        back_populates="atencion", cascade="all, delete-orphan", lazy="selectin", uselist=False
    )


# Imports al final para evitar import circular entre modelos relacionados.
from app.infrastructure.adapters.output.persistence.models.medicamento_model import MedicamentoModel  # noqa: E402
from app.infrastructure.adapters.output.persistence.models.evidencia_receta_model import (  # noqa: E402
    EvidenciaRecetaModel,
)
