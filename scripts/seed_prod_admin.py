from sqlalchemy.orm import Session
from app.models import User
from app.db import engine
from passlib.hash import argon2

def seed_admin():
    with Session(engine) as session:
        admin = session.query(User).filter_by(username="admin").first()
        if not admin:
            new_admin = User(username="admin", hashed_password=argon2.hash("admin"), role="admin")
            session.add(new_admin)
            session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    seed_admin()
