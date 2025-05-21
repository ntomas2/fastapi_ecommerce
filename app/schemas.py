from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class OutputModel(BaseModel):
    status_code: int
    message: str


class OutputProduct(OutputModel):
    pass


class OutputCategory(OutputModel):
    pass


class OutputUser(OutputModel):
    pass


class OutputToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category_id: int


class UpdateProduct(CreateProduct):
    name: str | None = None
    description: str | None = None
    price: int | None = None
    image_url: str | None = None
    stock: int | None = None
    category_id: int


class GetProduct(CreateProduct):
    slug: str
    rating: float
    # is_active: bool


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None


class UpdateCategory(CreateCategory):
    name: str
    parent_id: int | None = None


class GetCategory(CreateCategory):
    name: str
    slug: str
    parent_id: int | None
    is_active: bool
    


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str


class GetUser(BaseModel):
    username: str
    id: int
    user_role: str


class CreateComment(BaseModel):
    comment: str
    grade: int = Field(ge=0, le=5)
    product_id: int


class GetComment(CreateComment):
    id: int
    user_id: int
    comment_dt: datetime
    # is_active: bool
