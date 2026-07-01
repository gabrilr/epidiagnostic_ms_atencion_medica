"""
Modelo SQLAlchemy: MedicamentoModel

Tabla que persiste los medicamentos recetados, relacionados 1-a-muchos
con AtencionModel.
"""
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.config.database import Base
from app.infrastructure.config.types import GUID


class MedicamentoModel(Base):
    __tablename__ = "medicamentos"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    atencion_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("atenciones.id"), nullable=False, index=True
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    dosis: Mapped[str] = mapped_column(String(100), nullable=False)
    frecuencia: Mapped[str] = mapped_column(String(100), nullable=False)
    duracion: Mapped[str] = mapped_column(String(100), nullable=False)

    atencion: Mapped["AtencionModel"] = relationship(back_populates="medicamentos")
