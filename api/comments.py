from fastapi import APIRouter, Depends, HTTPException, status, Request
from domain.comment import CommentCreate, CommentOut, CommentUpdate
from service.comment_service import CommentService
from auth.dependencies import get_current_user
from typing import List

router = APIRouter()

def get_comment_service(request: Request) -> CommentService:
    return CommentService(request.app.state.mongo_db)

@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
        comment: CommentCreate,
        user=Depends(get_current_user),
        service: CommentService = Depends(get_comment_service)
):
    return await service.create_comment(comment, user)

@router.get("/post/{post_id}", response_model=List[CommentOut])
async def get_comments_for_post(
        post_id: str,
        service: CommentService = Depends(get_comment_service),
        user=Depends(get_current_user)
):
    return await service.list_comments_by_post(post_id)

@router.put("/{comment_id}", response_model=CommentOut)
async def update_comment(
        comment_id: str,
        update: CommentUpdate,
        user=Depends(get_current_user),
        service: CommentService = Depends(get_comment_service)
):
    return await service.update_comment(comment_id, update, user)

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        comment_id: str,
        user=Depends(get_current_user),
        service: CommentService = Depends(get_comment_service)
):
    await service.delete_comment(comment_id, user)
