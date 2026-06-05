from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserRegister, UserLogin
from app.core.events import seed_default_categories

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def register(self, data: UserRegister):
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        hashed = hash_password(data.password)
        user = await self.user_repo.create(email=data.email, hashed_password=hashed)
        await seed_default_categories(user.id, self.user_repo.db)
        return user

    async def login(self, data: UserLogin):
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        access_token = create_access_token(user.id)
        refresh_token = await self.token_repo.create(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def refresh(self, token_str: str):
        token = await self.token_repo.get_valid(token_str)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
        await self.token_repo.revoke(token_str)
        new_access = create_access_token(token.user_id)
        new_refresh = await self.token_repo.create(token.user_id)
        return {"access_token": new_access, "refresh_token": new_refresh}

    async def logout(self, token_str: str):
        await self.token_repo.revoke(token_str)