from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update
from starlette import status

from app.backend.db_depends import DBSessionDep
from app.models.user import User
from .auth import CurrentUserDep
from app.schemas import OutputModel


router = APIRouter(prefix='/permission', tags=['permission 🧑💻'])


@router.patch('/')
async def supplier_permission(db: DBSessionDep, get_user: CurrentUserDep, user_id: int) -> OutputModel:
    if get_user.user_role != 'is_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permission"
        )
    user = await db.scalar(select(User).where(User.id == user_id))
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    if user.user_role.value == 'is_supplier':
        await db.execute(update(User).where(User.id == user_id).values(user_role='is_customer'))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'message': 'User is no longer supplier'
        }
    await db.execute(update(User).where(User.id == user_id).values(user_role='is_supplier'))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'message': 'User is now supplier'
    }


@router.delete('/delete')
async def delete_user(db: DBSessionDep, get_user: CurrentUserDep, user_id: int) -> OutputModel:
    if get_user.user_role != 'is_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permission"
        )
    user = await db.scalar(select(User).where(User.id == user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't delete admin user"
        )
    if not user.is_active:
        return {
            'status_code': status.HTTP_200_OK,
            'message': 'User has already been deleted'
        }
    await db.execute(update(User).where(User.id == user_id).values(is_active=False))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'message': 'User is deleted'
    }
