from fastapi import APIRouter, Depends, HTTPException, status, Request
from domain.post import PostCreate, PostOut, PostUpdate
from service.post_service import PostService
from auth.dependencies import get_current_user
from typing import List, Optional

router = APIRouter()

def get_post_service(request: Request) -> PostService:
    return PostService(request.app.state.mongo_db)

@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
        post: PostCreate,
        request: Request,
        user=Depends(get_current_user),
        service: PostService = Depends(get_post_service)
):
    return await service.create_post(post, user)

@router.get("/", response_model=List[PostOut])
async def list_posts(
        request: Request,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        service: PostService = Depends(get_post_service),
        user=Depends(get_current_user)
):
    return await service.list_posts(search=search, skip=skip, limit=limit)

@router.get("/{post_id}", response_model=PostOut)
async def get_post(
        post_id: str,
        request: Request,
        service: PostService = Depends(get_post_service),
        user=Depends(get_current_user)
):
    return await service.get_post_by_id(post_id)

@router.put("/{post_id}", response_model=PostOut)
async def update_post(
        post_id: str,
        post: PostUpdate,
        request: Request,
        user=Depends(get_current_user),
        service: PostService = Depends(get_post_service)
):
    return await service.update_post(post_id, post, user)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id: str,
        request: Request,
        user=Depends(get_current_user),
        service: PostService = Depends(get_post_service)
):
    await service.delete_post(post_id, user)

@router.post("/{post_id}/vote")
async def vote_post(
        post_id: str,
        vote: str,
        request: Request,
        user=Depends(get_current_user),
        service: PostService = Depends(get_post_service)
):
    if vote not in ("up", "down"):
        raise HTTPException(status_code=400, detail="vote must be 'up' or 'down'")
    return await service.vote_post(post_id, vote, user)
