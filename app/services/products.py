from fastapi import Depends, HTTPException, status
from slugify import slugify
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models import *
from app.routers.auth import CurrentUserDep
from app.schemas import CreateProduct, OutputProduct, UpdateProduct


class ProductService:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session
    
    async def get_product_details(self, product_slug: str) -> Product:
        product = await self.session.scalar(select(Product)
                                            .where(
                                                Product.slug == product_slug,
                                                Product.is_active == True,
                                                Product.stock > 0))
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )
        return product
    
    async def get_all_products(self) -> list[Product]:
        products = await self.session.scalars(select(Product).join(Category)
                                              .where(
                                                  Product.is_active == True,
                                                  Category.is_active == True,
                                                  Product.stock > 0))
        products = products.all()
        if not products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There are no products'
            )
        return products
    
    async def get_products_by_category(self, category_slug: str) -> list[Product]:
        category = await self.session.scalar(select(Category)
                                             .where(Category.slug == category_slug))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Category not found'
            )
        subcategories = await self.session.scalars(select(Category)
                                                   .where(Category.parent_id == category.id))
        category_ids = [category.id] + [subcat.id for subcat in subcategories.all()]
        products = await self.session.scalars(select(Product)
                                              .where(
                                                  Product.category_id.in_(category_ids),
                                                  Product.is_active == True,
                                                  Product.stock > 0))
        return products.all()
    
    async def create_product(self, create_product: CreateProduct, get_user: CurrentUserDep) -> OutputProduct:
        if get_user.user_role == 'is_customer':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You are not authorized to use this method'
            )
        category = await self.session.scalar(select(Category)
                                             .where(Category.id == create_product.category_id))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        await self.session.execute(insert(Product)
                                   .values(
                                       **create_product.model_dump(),
                                        slug=slugify(create_product.name),
                                        supplier_id = get_user.id))
        await self.session.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'message': 'Successful'
        }

    async def update_product(self, product_slug: str,
                                   update_product_model: UpdateProduct,
                                   get_user: CurrentUserDep) -> OutputProduct:
        if get_user.user_role == 'is_customer':
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to use this method'
            )

        product_update = await self.session.scalar(select(Product).where(Product.slug == product_slug))
        if product_update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )

        if not (get_user.id == product_update.supplier_id or get_user.user_role == 'is_admin'):
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
            )
        category = await self.session.scalar(select(Category).where(Category.id == update_product_model.category_id))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        
        if update_product_model.name:
            await self.session.execute(update(Product)
                            .where(Product.id == product_update.id)
                            .values(**update_product_model.model_dump(exclude_none=True),
                                    slug=slugify(update_product_model.name)))
        else:
            await self.session.execute(update(Product)
                            .where(Product.id == product_update.id)
                            .values(**update_product_model.model_dump(exclude_none=True)))
        
        await self.session.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'message': 'Product update is successful'
        }

    async def delete_product(self,
                             product_slug: str,
                             get_user: CurrentUserDep) -> OutputProduct:
        if get_user.user_role == 'is_customer':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You are not authorized to use this method'
            )
        product_delete = await self.session.scalar(select(Product).where(Product.slug == product_slug))
        if product_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )
        if not (get_user.id == product_delete.supplier_id or get_user.user_role == 'is_admin'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You have not enough permission to for this action'
            )
        product_delete.is_active = False
        await self.session.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'message': 'Product delete is successful'
        }
