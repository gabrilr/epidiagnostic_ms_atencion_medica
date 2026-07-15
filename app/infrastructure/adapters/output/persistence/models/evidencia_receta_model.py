"""
Modelo SQLAlchemy: EvidenciaRecetaModel

Tabla 1-a-1 con AtencionModel. Guarda solo la URL de Cloudinary y su
public_id, nunca el binario de la imagen (eso vive en Cloudinary).
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.config.database import Base
from app.infrastructure.config.types import GUID


class EvidenciaRecetaModel(Base):
    __tablename__ = "evidencias_recetas"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    atencion_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("atenciones.id"), nullable=False, unique=True, index=True
    )
    url_imagen: Mapped[str] = mapped_column(String(1000), nullable=False)
    public_id_cloudinary: Mapped[str] = mapped_column(String(500), nullable=False)
    fecha_captura: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    atencion: Mapped["AtencionModel"] = relationship(back_populates="evidencia")
