from fastapi import APIRouter, status, HTTPException
from sqlalchemy import insert, select, update
from slugify import slugify

from app.backend.db_depends import DBSessionDep
from app.schemas import CreateCategory, GetCategory, OutputCategory, UpdateCategory
from app.models.category import Category
from .auth import CurrentUserDep


router = APIRouter(prefix='/category', tags=['category 🛍️'])


@router.get('/')
async def get_all_categories(db: DBSessionDep) -> list[GetCategory]:
    categories = await db.scalars(select(Category).where(Category.is_active == True))
    categories = categories.all()
    if not categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no categories yet'
        )
    return categories


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=OutputCategory)
async def create_category(db: DBSessionDep,
                          create_category: CreateCategory,
                          get_user: CurrentUserDep) -> OutputCategory:
    if get_user.user_role != 'is_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be admin user for this'
        )
    await db.execute(insert(Category).values(**create_category.model_dump(),
                                             slug=slugify(create_category.name)))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'message': 'Successful'
    }


@router.put('/', response_model=OutputCategory)
async def update_category(db: DBSessionDep,
                          category_id: int,
                          update_category: UpdateCategory,
                          get_user: CurrentUserDep) -> OutputCategory:
    if get_user.user_role != 'is_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be admin user for this'
        )
    category = await db.scalar(select(Category).where(Category.id == category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )

    await db.execute(update(Category)
                    .where(Category.id == category.id)
                    .values(**update_category.model_dump(exclude_none=True),
                            slug=slugify(update_category.name)))
    await db.commit()
    
    return {
        'status_code': status.HTTP_200_OK,
        'message': 'Category update is successful'
    }
    

@router.delete('/', response_model=OutputCategory)
async def delete_category(db: DBSessionDep,
                          category_id: int,
                          get_user: CurrentUserDep) -> OutputCategory:
    if get_user.user_role != 'is_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be admin user for this'
        )
    category = await db.scalar(select(Category).where(Category.id == category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    category.is_active = False
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'message': 'Category delete is successful'
    }
