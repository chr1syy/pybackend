from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Float,
    Boolean,
    Date,
    DateTime, 
    ForeignKey, 
    JSON
)
from sqlalchemy.orm import relationship

from datetime import datetime

from app.utils.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")

    # Metadaten
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    access_codes = relationship("AccessCode", back_populates="user")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="refresh_tokens", passive_deletes=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    details = Column(JSON, nullable=True)  # Zusatzinfos (z.B. welche Felder geändert wurden)

    user = relationship("User", back_populates="audit_logs")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_number = Column(String, unique=True, nullable=False)  # Format YYYY-XXXX
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Beziehung zu CableCalculation
    cable_calculations = relationship(
        "CableCalculation",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    owner = relationship("User")

class AccessCode(Base):
    """
    Für Registrierung, E-Mail-Verifikation oder einmalige Codes.
    """
    __tablename__ = "access_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, index=True)
    purpose = Column(String, nullable=False)  # "registration", "email_verification"
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="access_codes")

class PasswordResetToken(Base):
    """
    Für Passwort-vergessen / Reset-Flow.
    """
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="password_reset_tokens")


class CableCalculation(Base):
    __tablename__ = "cable_calculations"

    id = Column(Integer, primary_key=True, index=True)

    # Projektbezug + Versionierung
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Technische Angaben
    origin = Column(String, nullable=False)              # Ursprung (z. B. Trafo)
    destination = Column(String, nullable=False)         # Zielverbraucher (z. B. H10)
    cable_type = Column(String, nullable=False)          # z. B. NYCWY
    cable_length_m = Column(Float, nullable=False)       # Leitungslänge in Meter
    number_of_cables = Column(Integer, nullable=False)   # Anzahl Leitungen
    total_cores = Column(Integer, nullable=False)        # Adern insgesamt
    loaded_cores = Column(Integer, nullable=False)       # Adern belastet

    cross_section_l = Column(Float, nullable=False)      # Querschnitt L1/L2/L3/N
    cross_section_pe = Column(Float, nullable=False)     # Querschnitt PE

    laying_type = Column(String, nullable=False)         # Verlegeart (z. B. D)
    fuse_rating_a = Column(Float, nullable=False)        # Nennstrom Absicherung (A)
    nominal_current_a = Column(Float, nullable=False)    # Betriebsstrom Verbraucher (A)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Optional: Beziehung zum Projekt
    project = relationship("Project", back_populates="cable_calculations")
    owner = relationship("User")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # z.B. "KG 445 Beleuchtungsanlagen"

    # Beziehung zu Artikeln
    articles = relationship("Article", back_populates="category", cascade="all, delete-orphan")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Artikelname
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Beziehung zu Kategorie
    category = relationship("Category", back_populates="articles")

    # Beziehung zu Preisen
    prices = relationship("Price", back_populates="article", cascade="all, delete-orphan")


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    price = Column(Float, nullable=False)   # Preiswert
    date = Column(Date, nullable=False)     # Datum des Angebots

    # Beziehung zu Artikel
    article = relationship("Article", back_populates="prices")

