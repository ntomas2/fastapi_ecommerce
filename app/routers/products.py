from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy import insert, select
from slugify import slugify

from app.backend.db_depends import get_db
from app.schemas import CreateProduct
from app.models import *

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(Product).join(Category).where(Product.is_active == True,
                                                               Category.is_active == True,
                                                               Product.stock > 0))
    if products is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no products'
        )
    return products.all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct):
    category = await db.scalar(select(Category).where(Category.id == create_product.category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    await db.execute(insert(Product).values(name=create_product.name,
                                            slug=slugify(create_product.name),
                                            description = create_product.description,
                                            price=create_product.price,
                                            image_url=create_product.image_url,
                                            stock=create_product.stock,
                                            category_id=create_product.category_id,
                                            rating=0.0))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get('/{category_slug}')
async def product_by_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
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
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug,
                                                    Product.is_active == True,
                                                    Product.stock > 0))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    return product


@router.put('/{product_slug}')
async def update_product_model(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, update_product_model: CreateProduct):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    category = await db.scalar(select(Category).where(Category.id == update_product_model.category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    
    product.name = update_product_model.name
    product.description = update_product_model.description
    product.price = update_product_model.price
    product.image_url = update_product_model.image_url
    product.stock = update_product_model.stock
    product.category_id = update_product_model.category_id
    product.slug = slugify(update_product_model.name)
    
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Product update is successful'
    }


@router.delete('/{product_slug}')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product_delete = await db.scalar(select(Product).where(Product.slug == product_slug, Product.is_active == True))
    if product_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    product_delete.is_active = False
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product delete is successful'
    }
