import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
from app.core.config import settings

class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int) -> str:
        token_str = secrets.token_urlsafe(64)
        expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token = RefreshToken(user_id=user_id, token=token_str, expires_at=expires)
        self.db.add(token)
        await self.db.commit()
        return token_str

    async def get_valid(self, token_str: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token == token_str,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, token_str: str):
        token = await self.get_valid(token_str)
        if token:
            token.revoked = True
            await self.db.commit()