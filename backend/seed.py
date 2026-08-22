"""
One-off script to:
  1. Create the 'admin' and 'user' roles if missing.
  2. Create a default admin account so you can log in immediately.

Run with:  python seed.py
(Run this AFTER the FastAPI app has started at least once, or after
 running create_all — both create the tables. Simplest: just run
 `uvicorn app.main:app` once, stop it, then run this script.)
"""
from app.db.database import SessionLocal, Base, engine
import app.models  # noqa: F401  (registers every table with Base.metadata)
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    for role_name in ("admin", "user"):
        if not db.query(Role).filter(Role.name == role_name).first():
            db.add(Role(name=role_name))
    db.commit()

    admin_role = db.query(Role).filter(Role.name == "admin").first()

    default_admin_email = "admin@example.com"
    if not db.query(User).filter(User.email == default_admin_email).first():
        admin_user = User(
            name="Default Admin",
            email=default_admin_email,
            hashed_password=hash_password("Admin@123"),
            role_id=admin_role.id,
        )
        db.add(admin_user)
        db.commit()
        print(f"Created default admin -> email: {default_admin_email}  password: Admin@123")
    else:
        print("Default admin already exists.")

    print("Seed complete. Roles ensured: admin, user.")
finally:
    db.close()
