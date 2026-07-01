"""
Tipo de columna GUID portable (mismo patrón usado en el Microservicio 1
de Pacientes y Personal, ver app/infrastructure/config/types.py allá).

Se duplica aquí intencionalmente: cada microservicio es independiente
(Database per service) y no comparte código de infraestructura entre
sí, solo contratos HTTP. Si en el futuro se decide compartir esta
utilidad, debería extraerse a un paquete Python común versionado, no
importarse directamente entre microservicios.
"""
import uuid

from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)
