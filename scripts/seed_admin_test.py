# scripts/seed_admin_test.py
# Special version for testing with a known password
from sqlalchemy.orm import Session

from app.utils.db import SessionLocal, Base, engine
from app.models import User, RefreshToken

from passlib.hash import argon2

# Test-specific password that meets all security requirements
TEST_ADMIN_PASSWORD = "TestAdmin123!Secure"

def seed_admin_test():
    """Seed admin user with a known password for testing purposes."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    # Check if admin exists
    admin = db.query(User).filter_by(email="admin@example.com").first()
    if not admin:
        # Optional: delete old tokens/users if desired
        db.query(RefreshToken).delete()
        db.query(User).delete()
        db.commit()

        # Create admin with test password
        new_admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=argon2.hash(TEST_ADMIN_PASSWORD),
            role="admin",
            is_active=True,
            email_verified=True
        )
        db.add(new_admin)
        db.commit()
        print(f"Test admin created with password: {TEST_ADMIN_PASSWORD}")
    else:
        print("Admin user already exists.")

    db.close()

if __name__ == "__main__":
    seed_admin_test()
