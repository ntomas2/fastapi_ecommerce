from pydantic import BaseModel, EmailStr, Field


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category_id: int


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str


class CreateComment(BaseModel):
    comment: str
    grade: int = Field(ge=0, le=5)
    product_id: int
