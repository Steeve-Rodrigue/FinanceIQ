from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import engine, get_db
from app.main import app


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """One outer transaction per test, rolled back at teardown.

    Opens a connection, begins an outer transaction on it, and binds a session to that
    connection so anything the app does during the test (including nested commits) stays
    inside the outer transaction. `app.dependency_overrides[get_db]` is pointed at this
    session for the duration of the test so the real `get_db` dependency (and its own
    session/engine) is never touched.
    """
    async with engine.connect() as connection:
        outer_transaction = await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        session = session_factory()

        async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
            yield session

        app.dependency_overrides[get_db] = _override_get_db
        try:
            yield session
        finally:
            app.dependency_overrides.pop(get_db, None)
            await session.close()
            await outer_transaction.rollback()
