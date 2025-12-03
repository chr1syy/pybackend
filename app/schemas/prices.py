from pydantic import BaseModel
from datetime import date

# --- Category ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    class Config:
        orm_mode = True


# --- Article ---
class ArticleBase(BaseModel):
    name: str

class ArticleCreate(ArticleBase):
    category_id: int

class ArticleRead(ArticleBase):
    id: int
    category_id: int
    class Config:
        orm_mode = True


# --- Price ---
class PriceBase(BaseModel):
    price: float
    date: date

class PriceCreate(PriceBase):
    article_id: int

class PriceRead(PriceBase):
    id: int
    article_id: int
    class Config:
        orm_mode = True
