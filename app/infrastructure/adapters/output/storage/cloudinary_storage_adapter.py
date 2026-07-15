"""
Adaptador de salida: CloudinaryStorageAdapter

Implementación concreta de EvidenciaStoragePort usando el SDK oficial
de Cloudinary. Sube la imagen recibida en base64 y devuelve la URL
pública (segura, HTTPS) más el public_id, que se guarda para poder
referenciar/eliminar la imagen después.

Decisión de diseño confirmada: se usa un servicio externo porque el
servidor/API siempre tiene conectividad (a diferencia del celular
offline-first, que es el que tiene restricciones de red).
"""
import cloudinary
import cloudinary.uploader

from app.application.ports.evidencia_storage_port import EvidenciaStoragePort, EvidenciaSubidaDTO
from app.domain.exceptions.domain_exceptions import EvidenciaInvalidaException
from app.infrastructure.config.settings import get_settings

settings = get_settings()

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


class CloudinaryStorageAdapter(EvidenciaStoragePort):

    async def subir_evidencia(self, imagen_base64: str, atencion_id: str) -> EvidenciaSubidaDTO:
        try:
            # cloudinary.uploader.upload acepta directamente un data URI
            # base64 (ej. "data:image/jpeg;base64,...") o el string base64
            # puro; el SDK no es async nativo, pero la llamada es rápida
            # y no bloquea significativamente en este volumen de uso.
            # TODO: si el volumen de subidas crece, envolver esta llamada
            # con asyncio.to_thread() para no bloquear el event loop.
            resultado = cloudinary.uploader.upload(
                imagen_base64,
                folder=f"epidiagnostic-maya/evidencias-recetas/{atencion_id}",
                resource_type="image",
            )
        except Exception as error:
            raise EvidenciaInvalidaException(detalle=str(error)) from error

        return EvidenciaSubidaDTO(
            url_imagen=resultado["secure_url"],
            public_id=resultado["public_id"],
        )
