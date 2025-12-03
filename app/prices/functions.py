from sqlalchemy.orm import Session
from app.models import Category, Article, Price
from app.schemas.prices import CategoryCreate, ArticleCreate, PriceCreate

# --- Category ---
def create_category(db: Session, category: CategoryCreate):
    db_cat = Category(**category.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

def get_categories(db: Session):
    return db.query(Category).all()

def update_category(db: Session, cat_id: int, category: CategoryCreate):
    db_cat = db.query(Category).filter_by(id=cat_id).first()
    if not db_cat:
        return None
    db_cat.name = category.name
    db.commit()
    db.refresh(db_cat)
    return db_cat

def delete_category(db: Session, cat_id: int):
    db_cat = db.query(Category).filter_by(id=cat_id).first()
    if not db_cat:
        return None
    db.delete(db_cat)
    db.commit()
    return True


# --- Article ---
def create_article(db: Session, article: ArticleCreate):
    db_article = Article(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_articles_by_category(db: Session, category_id: int):
    return db.query(Article).filter_by(category_id=category_id).all()

def update_article(db: Session, article_id: int, article: ArticleCreate):
    db_article = db.query(Article).filter_by(id=article_id).first()
    if not db_article:
        return None
    db_article.name = article.name
    db_article.category_id = article.category_id
    db.commit()
    db.refresh(db_article)
    return db_article

def delete_article(db: Session, article_id: int):
    db_article = db.query(Article).filter_by(id=article_id).first()
    if not db_article:
        return None
    db.delete(db_article)
    db.commit()
    return True


# --- Price ---
def create_price(db: Session, price: PriceCreate):
    db_price = Price(**price.dict())
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

def get_prices_by_article(db: Session, article_id: int):
    return db.query(Price).filter_by(article_id=article_id).all()

def delete_price(db: Session, price_id: int):
    db_price = db.query(Price).filter_by(id=price_id).first()
    if not db_price:
        return None
    db.delete(db_price)
    db.commit()
    return True
