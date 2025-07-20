import logging
from uuid import uuid4

from fastapi import HTTPException, status
from passlib.context import CryptContext

from domain.user import UserCreate, UserLogin, TokenOut
from cached_repositories.user_cache_repo import UserCacheRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth.jwt_handler import create_access_token

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._repo = UserCacheRepository(db)

    @property
    def repo(self) -> UserCacheRepository:
        if self._repo is None:
            try:
                self._repo = UserCacheRepository()
            except Exception as e:
                logger.error(f"Failed to initialize UserCacheRepository: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Could not access user repository")
        return self._repo

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def register_user(self, user: UserCreate) -> TokenOut:
        """
        Register a new user and return access token.
        """
        try:
            existing = await self.repo.get_user_by('username', user.username)
            if existing:
                logger.warning(f"Username already taken: {user.username}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

            user_id = str(uuid4())
            password_hash = self.hash_password(user.password)

            new_user = {
                "id": user_id,
                "username": user.username,
                "password_hash": password_hash
            }

            await self.repo.save_user(new_user)
            logger.info(f"User registered successfully: {user.username} ({user_id})")

            token = create_access_token(user_id)
            return TokenOut(access_token=token, token_type="bearer")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to register user {user.username}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    async def login_user(self, user: UserLogin) -> TokenOut:
        """
        Authenticate user and return access token.
        """
        try:
            db_user = await self.repo.get_user_by('username', user.username)
            if not db_user:
                logger.warning(f"Login failed: user not found - {user.username}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            if not self.verify_password(user.password, db_user["password_hash"]):
                logger.warning(f"Login failed: incorrect password - {user.username}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            logger.info(f"User logged in: {user.username}")
            token = create_access_token(db_user["id"])
            return TokenOut(access_token=token, token_type="bearer")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to log in user {user.username}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
