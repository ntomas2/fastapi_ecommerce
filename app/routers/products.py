from fastapi import APIRouter, status, Depends

from app.schemas import CreateProduct, GetProduct, OutputProduct, UpdateProduct
from app.models import *
from .auth import CurrentUserDep
from app.services.products import ProductService


router = APIRouter(prefix='/products', tags=['products 📦'])


@router.get('/')
async def all_products(service: ProductService = Depends()) -> list[GetProduct]:
    return await service.get_all_products()


@router.get('/{category_slug}')
async def product_by_category(category_slug: str, service: ProductService = Depends()) -> list[GetProduct]:
    return await service.get_products_by_category(category_slug)
    

@router.get('/detail/{product_slug}')
async def product_detail(product_slug: str, service: ProductService = Depends()) -> GetProduct:
    return await service.get_product_details(product_slug)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=OutputProduct)
async def create_product(create_product: CreateProduct,
                         get_user: CurrentUserDep,
                         service: ProductService = Depends()) -> OutputProduct:
    return await service.create_product(create_product=create_product, get_user=get_user)


@router.put('/detail/{product_slug}', response_model=OutputProduct)
async def update_product_model(product_slug: str,
                               update_product_model: UpdateProduct,
                               get_user: CurrentUserDep,
                               service: ProductService = Depends()) -> OutputProduct:
    return await service.update_product(product_slug=product_slug,
                                        update_product_model=update_product_model,
                                        get_user=get_user)


@router.delete('/', response_model=OutputProduct)
async def delete_product(product_slug: str,
                         get_user: CurrentUserDep,
                         service: ProductService = Depends()) -> OutputProduct:
    return await service.delete_product(product_slug=product_slug, get_user=get_user)
