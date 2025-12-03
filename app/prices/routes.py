from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.utils.db import get_db
from app.utils.auth import get_current_user

from app.schemas.prices import CategoryCreate, CategoryRead, ArticleCreate, ArticleRead, PriceCreate, PriceRead

from app.prices.functions import (
    create_category, get_categories, update_category, delete_category,
    create_article, get_articles_by_category, update_article, delete_article,
    create_price, get_prices_by_article, delete_price
)

router = APIRouter()

# --- Category ---
@router.post("/categories", response_model=CategoryRead)
def add_category(category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_category(db, category)

@router.get("/categories", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return get_categories(db)

@router.put("/categories/{cat_id}", response_model=CategoryRead)
def edit_category(cat_id: int, category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = update_category(db, cat_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.delete("/categories/{cat_id}")
def remove_category(cat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted = delete_category(db, cat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"detail": "Category deleted"}


# --- Article ---
@router.post("/articles", response_model=ArticleRead)
def add_article(article: ArticleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_article(db, article)

@router.get("/categories/{category_id}/articles", response_model=list[ArticleRead])
def list_articles(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_articles_by_category(db, category_id)

@router.put("/articles/{article_id}", response_model=ArticleRead)
def edit_article(article_id: int, article: ArticleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = update_article(db, article_id, article)
    if not updated:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated

@router.delete("/articles/{article_id}")
def remove_article(article_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted = delete_article(db, article_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"detail": "Article deleted"}


# --- Price ---
@router.post("/prices", response_model=PriceRead)
def add_price(price: PriceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_price(db, price)

@router.get("/articles/{article_id}/prices", response_model=list[PriceRead])
def list_prices(article_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_prices_by_article(db, article_id)

@router.delete("/prices/{price_id}")
def remove_price(price_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted = delete_price(db, price_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Price not found")
    return {"detail": "Price deleted"}
