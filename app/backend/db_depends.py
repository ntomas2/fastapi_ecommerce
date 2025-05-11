from typing import AsyncGenerator, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.backend.db import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
