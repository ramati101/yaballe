from fastapi import APIRouter, Depends, HTTPException, status, Request
from domain.user import UserCreate, UserLogin, TokenOut
from service.user_service import UserService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def get_user_service(request: Request) -> UserService:
    db = request.app.state.mongo_db
    return UserService(db)

@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    try:
        return await service.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

@router.post("/login", response_model=TokenOut)
async def login_user(user: UserLogin, service: UserService = Depends(get_user_service)):
    try:
        return await service.login_user(user)
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Login failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")
