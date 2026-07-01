"""
Settings del Microservicio de Atención Médica.

Además de la configuración de base de datos (igual patrón que MS1),
incluye:
- La URL base del Microservicio 1, usada por los clientes HTTP
  (pacientes_client.py, personal_client.py) para validar paciente_id y
  personal_id.
- Credenciales de Cloudinary, usadas por cloudinary_storage_adapter.py
  para subir evidencia de recetas.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "EpiDiagnostic-Maya · Microservicio de Atención Médica"
    environment: str = "development"

    database_url: str = "mysql+aiomysql://root:root@db:3306/atencion_medica_db"
    db_echo: bool = False

    # URL del Microservicio 1 (Pacientes y Personal). Dentro de
    # docker-compose, si ambos microservicios comparten red, el host
    # sería el nombre del servicio (ej. "ms-pacientes-api"); si corren
    # en hosts/proyectos docker-compose distintos, usar la IP/dominio
    # real donde esté publicado el MS1.
    ms_pacientes_base_url: str = "http://localhost:8000"
    ms_pacientes_timeout_seconds: float = 5.0

    # Credenciales de Cloudinary (obtener del dashboard:
    # https://cloudinary.com/console).
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
