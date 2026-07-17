"""
Configuración de base de datos: engine, sesión y Base declarativa.

Mismo patrón que MS1: SQLAlchemy async con aiomysql para MySQL.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Parche de compatibilidad para evitar TypeError en pool_pre_ping con PyMySQL >= 1.2.0 y aiomysql.
# PyMySQL >= 1.2.0 cambia la firma/valor predeterminado de ping(), provocando que SQLAlchemy
# llame a ping() sin argumentos, lo cual falla en el adaptador de aiomysql. Espejo del mismo
# parche en MS1 (ver database.py de ms_pacientes).
try:
    from sqlalchemy.dialects.mysql.aiomysql import AsyncAdapt_aiomysql_connection
    _original_ping = AsyncAdapt_aiomysql_connection.ping
    def _patched_ping(self, reconnect=True):
        return _original_ping(self, reconnect)
    AsyncAdapt_aiomysql_connection.ping = _patched_ping
except ImportError:
    pass

from app.infrastructure.config.settings import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
