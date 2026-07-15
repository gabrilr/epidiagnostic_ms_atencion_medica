"""
Entidad: EvidenciaReceta

Entidad interna del agregado Atencion. Guarda únicamente la REFERENCIA
(URL) a la imagen de la receta, nunca el binario de la imagen — el
binario vive en Cloudinary (servicio externo de almacenamiento de
imágenes), subido por el adaptador de salida
infrastructure/adapters/output/storage/cloudinary_storage_adapter.py.

Decisión de diseño: se usa un servicio externo (Cloudinary) en vez de
almacenamiento local porque el servidor/API SIEMPRE tiene conectividad
(a diferencia del celular offline-first) — es la app móvil la que no
tiene internet garantizado, no el microservicio.
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EvidenciaReceta:
    url_imagen: str
    public_id_cloudinary: str  # identificador de Cloudinary, útil para eliminar/reemplazar la imagen después
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    fecha_captura: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.url_imagen or not self.url_imagen.strip():
            raise ValueError("La URL de la evidencia no puede estar vacía.")
