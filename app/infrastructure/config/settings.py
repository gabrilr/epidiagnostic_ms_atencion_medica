"""
Settings del Microservicio de Atención Médica.

Además de la configuración de base de datos (igual patrón que los demás
microservicios), incluye:
- JWT_SECRET_KEY/JWT_ALGORITHM: DEBEN tener el mismo valor que en
  ms-personal (MS3), que es quien emite los tokens. MS2 no tiene su
  propio sistema de login — decodifica el mismo JWT de forma stateless,
  sin llamar de vuelta a MS3 para validar el token (ver
  auth_dependencies.py).
- `ms_pacientes_base_url`: usada por pacientes_client.py para validar
  paciente_id contra ms-pacientes (MS1).
- `ms_personal_base_url`: usada por personal_client.py para validar
  personal_id contra ms-personal (MS3) — antes de la separación en 4
  microservicios, esto vivía en el mismo servicio que pacientes_client.py
  apuntaba, por eso hoy son dos URLs/clientes distintos.
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

    # JWT — mismo valor que JWT_SECRET_KEY/JWT_ALGORITHM en ms-personal (MS3).
    jwt_secret_key: str = "cambia-este-secreto-en-produccion"
    jwt_algorithm: str = "HS256"

    # URL de ms-pacientes (MS1), usada por pacientes_client.py para
    # validar paciente_id. Dentro de docker-compose, si los
    # microservicios comparten red, el host sería el nombre del
    # servicio; si corren en proyectos docker-compose distintos, usar
    # la IP/dominio real donde esté publicado MS1.
    ms_pacientes_base_url: str = "http://localhost:8000"
    ms_pacientes_timeout_seconds: float = 5.0

    # URL de ms-personal (MS3), usada por personal_client.py para
    # validar personal_id. Antes de la separación en 4 microservicios,
    # GET /personal/{id} vivía en el mismo servicio que /pacientes/{id}
    # — ahora son destinos distintos.
    ms_personal_base_url: str = "http://localhost:8002"
    ms_personal_timeout_seconds: float = 5.0

    # Credenciales de Cloudinary (obtener del dashboard:
    # https://cloudinary.com/console).
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
