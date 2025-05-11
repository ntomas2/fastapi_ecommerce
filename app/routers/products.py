from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy import insert, select, update
from slugify import slugify

from app.backend.db_depends import DBSessionDep
from app.schemas import CreateProduct, GetProduct, OutputProduct, UpdateProduct
from app.models import *
from .auth import CurrentUserDep


router = APIRouter(prefix='/products', tags=['products 📦'])


@router.get('/')
async def all_products(db: DBSessionDep) -> list[GetProduct]:
    products = await db.scalars(select(Product).join(Category).where(Product.is_active == True,
                                                               Category.is_active == True,
                                                               Product.stock > 0))
    products = products.all()
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no products'
        )
    return products


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=OutputProduct)
async def create_product(db: DBSessionDep,
                         create_product: CreateProduct,
                         get_user: CurrentUserDep) -> OutputProduct:
    if not (get_user.get('is_admin') or get_user.get('is_supplier')):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to use this method'
        )
    category = await db.scalar(select(Category).where(Category.id == create_product.category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    await db.execute(insert(Product).values(**create_product.model_dump(),
                                            slug=slugify(create_product.name),
                                            supplier_id = get_user.get('id')))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'message': 'Successful'
    }


@router.get('/{category_slug}')
async def product_by_category(db: DBSessionDep, category_slug: str) -> list[GetProduct]:
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    subcategories = await db.scalars(select(Category).where(Category.parent_id == category.id))
    category_ids = [category.id] + [subcat.id for subcat in subcategories.all()]
    products = await db.scalars(select(Product).where(Product.category_id.in_(category_ids),
                                                      Product.is_active == True,
                                                      Product.stock > 0))
    return products.all()
    

@router.get('/detail/{product_slug}')
async def product_detail(db: DBSessionDep, product_slug: str) -> GetProduct:
    product = await db.scalar(select(Product).where(Product.slug == product_slug,
                                                    Product.is_active == True,
                                                    Product.stock > 0))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    return product


@router.put('/detail/{product_slug}', response_model=OutputProduct)
async def update_product_model(db: DBSessionDep,
                               product_slug: str,
                               update_product_model: UpdateProduct,
                               get_user: CurrentUserDep) -> OutputProduct:
    if not (get_user.get('is_supplier') or get_user.get('is_admin')):
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='You are not authorized to use this method'
        )

    product_update = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )

    if not (get_user.get('id') == product_update.supplier_id or get_user.get('is_admin')):
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='You have not enough permission for this action'
        )
    category = await db.scalar(select(Category).where(Category.id == update_product_model.category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    
    if update_product_model.name:
        await db.execute(update(Product)
                        .where(Product.id == product_update.id)
                        .values(**update_product_model.model_dump(exclude_none=True),
                                slug=slugify(update_product_model.name)))
    else:
        await db.execute(update(Product)
                        .where(Product.id == product_update.id)
                        .values(**update_product_model.model_dump(exclude_none=True)))
    
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'message': 'Product update is successful'
    }


@router.delete('/', response_model=OutputProduct)
async def delete_product(db: DBSessionDep,
                         product_slug: str,
                         get_user: CurrentUserDep) -> OutputProduct:
    if not (get_user.get('is_supplier') or get_user.get('is_admin')):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to use this method'
        )
    product_delete = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    if not (get_user.get('id') == product_delete.supplier_id or get_user.get('is_admin')):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission to for this action'
        )
    product_delete.is_active = False
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'message': 'Product delete is successful'
    }
