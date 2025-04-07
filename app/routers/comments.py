from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.backend.db_depends import get_db
from app.schemas import CreateComment
from app.models import *
from app.models.comments import Comment
from .auth import get_current_user


router = APIRouter(prefix='/comments', tags=['comments'])


@router.get('/')
async def all_comments(db: Annotated[AsyncSession, Depends(get_db)]):
    comments = await db.scalars(select(Comment).where(Comment.is_active == True))
    comments = comments.all()
    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no comments'
        )
    return comments


@router.get('/detail/{product_id}')
async def comment_detail(db: Annotated[AsyncSession, Depends(get_db)],
                         product_id: int):
    product = await db.scalar(select(Product).where(Product.id == product_id,
                                                    Product.is_active == True))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    comment_list = await db.scalars(select(Comment).where(Comment.product_id == product_id,
                                                              Comment.is_active == True))
    comment_list = comment_list.all()
    if not comment_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product comments'
        )
    return comment_list


@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_comment(db: Annotated[AsyncSession, Depends(get_db)],
                     create_comment: CreateComment,
                     get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user:
        product = await db.scalar(select(Product).where(Product.id == create_comment.product_id,
                                                        Product.is_active == True,
                                                        Product.stock > 0))
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )
        comment = await db.scalar(select(Comment).where(Comment.user_id == get_user.get('id'),
                                                        Comment.product_id == create_comment.product_id))
        if comment is None:
            await db.execute(insert(Comment).values(user_id=get_user.get('id'),
                                                    product_id=create_comment.product_id,
                                                    comment=create_comment.comment,
                                                    grade=create_comment.grade))
        else:
            comment.comment = create_comment.comment
            comment.grade = create_comment.grade
        product_comments_avg_grade = await db.scalar(select(func.avg(Comment.grade))
                                                     .where(Comment.product_id == create_comment.product_id))
        product.rating = product_comments_avg_grade
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'detail': 'Comment added successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be authorized user to add comment'
        )


@router.delete('/')
async def delete_comment(db: Annotated[AsyncSession, Depends(get_db)],
                         comment_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        comment_delete = await db.scalar(select(Comment).where(Comment.id == comment_id))
        if comment_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Comment not found'
            )
        if comment_delete.is_active == False:
            return {
                'status_code': status.HTTP_200_OK,
                'detail': 'Comment has already been deleted'
            }
        comment_delete.is_active = False
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'detail': 'Comment delete is successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be admin user for this action'
        )
