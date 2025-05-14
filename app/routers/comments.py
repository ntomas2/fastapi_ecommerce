from fastapi import APIRouter, status, HTTPException
from sqlalchemy import select, insert
from sqlalchemy import func

from app.backend.db_depends import DBSessionDep
from app.schemas import CreateComment, GetComment, OutputModel
from app.models import *
from app.models.comments import Comment
from .auth import CurrentUserDep


router = APIRouter(prefix='/comments', tags=['comments 💬'])


@router.get('/')
async def all_comments(db: DBSessionDep) -> list[GetComment]:
    comments = await db.scalars(select(Comment).where(Comment.is_active == True))
    comments = comments.all()
    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no comments'
        )
    return comments


@router.get('/detail/{product_id}')
async def comment_detail(db: DBSessionDep, product_id: int) -> list[GetComment]:
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
async def add_comment(db: DBSessionDep,
                     create_comment: CreateComment,
                     get_user: CurrentUserDep) -> OutputModel:
    if not get_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be authorized user to add comment'
        )
    product = await db.scalar(select(Product).where(Product.id == create_comment.product_id,
                                                    Product.is_active == True,
                                                    Product.stock > 0))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    comment = await db.scalar(select(Comment).where(Comment.user_id == get_user.id,
                                                    Comment.product_id == create_comment.product_id))
    if comment is None:
        await db.execute(insert(Comment).values(user_id=get_user.id,
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
        'message': 'Comment added successful'
    }


@router.delete('/')
async def delete_comment(db: DBSessionDep,
                         comment_id: int,
                         get_user: CurrentUserDep) -> OutputModel:
    if get_user.user_role != 'is_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be admin user for this action'
        )
    comment_delete = await db.scalar(select(Comment).where(Comment.id == comment_id))
    if comment_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Comment not found'
        )
    if comment_delete.is_active == False:
        return {
            'status_code': status.HTTP_200_OK,
            'message': 'Comment has already been deleted'
        }
    comment_delete.is_active = False
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'message': 'Comment delete is successful'
    }
