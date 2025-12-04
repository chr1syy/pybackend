from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

from app.core.settings import settings

env_mode = settings.ENV
# Use 127.0.0.1 instead of localhost to force TCP connection (not Unix socket)
host = "db" if env_mode == "production" else "127.0.0.1"

# URL-encode the password to handle special characters
DATABASE_URL=f"postgresql+psycopg2://{settings.POSTGRES_USER}:{quote_plus(settings.POSTGRES_PASSWORD)}@{host}:5432/{settings.POSTGRES_DB}"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Only enable echo in development mode for debugging
echo_sql = env_mode == "development"
engine = create_engine(DATABASE_URL, echo=echo_sql, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

