"""
Dependencias de autenticación del Microservicio de Atención Médica.

MS2 no tiene su propio login: valida el mismo JWT que emite MS1
(POST /auth/login), decodificándolo con la MISMA llave compartida
(JWT_SECRET_KEY) — validación stateless, sin llamar de vuelta a MS1
para confirmar que el token es válido.

Además de identificar al personal autenticado (get_personal_id_actual,
para proteger los endpoints propios de MS2), expone el token crudo
(get_bearer_token_actual) para reenviarlo hacia MS1 cuando este
microservicio necesita validar paciente_id/personal_id — ver
PacienteClient/PersonalClient. MS2 no tiene una identidad de servicio
propia registrada en MS1, así que propaga la credencial del personal
que originó la petición en vez de autenticarse por su cuenta.
"""
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.infrastructure.config.settings import get_settings

settings = get_settings()
_bearer_scheme = HTTPBearer()


def _credenciales_invalidas() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_personal_id_actual(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> UUID:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return UUID(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise _credenciales_invalidas()


async def get_bearer_token_actual(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    return credentials.credentials
