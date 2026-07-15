"""
Puerto de salida: EvidenciaStoragePort

Define el contrato para subir la imagen de evidencia de receta a un
almacenamiento externo, sin que el dominio/aplicación sepan que el
proveedor real es Cloudinary. Si en el futuro se cambia de proveedor
(ej. a S3/MinIO), solo se reemplaza la implementación
(cloudinary_storage_adapter.py), sin tocar casos de uso.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EvidenciaSubidaDTO:
    url_imagen: str
    public_id: str


class EvidenciaStoragePort(ABC):

    @abstractmethod
    async def subir_evidencia(self, imagen_base64: str, atencion_id: str) -> EvidenciaSubidaDTO:
        """
        Sube la imagen (recibida en base64 desde el celular) al storage
        externo y devuelve la URL pública y el identificador del
        proveedor. `atencion_id` se usa para nombrar/organizar la imagen
        en el storage (ej. carpeta por atención en Cloudinary).
        """
        raise NotImplementedError
