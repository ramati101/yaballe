from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
import logging
from typing import Dict
from cached_repositories.user_cache_repo import UserCacheRepository

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

async def get_current_user(request: Request,token: str = Depends(oauth2_scheme)) -> Dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("JWT missing 'sub'")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

        db = request.app.state.mongo_db
        repo = UserCacheRepository(db)
        user = await repo.get_user_by("id", user_id)
        if user is None:
            logger.warning(f"Token user not found: {user_id}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")

        return user

    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

    except Exception as e:
        logger.error(f"get_current_user failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal error")
