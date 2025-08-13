# app/seeds/users.py

import asyncio
from sqlalchemy import text
from sqlalchemy.future import select
from utils.db import AsyncSessionLocal, Base, engine
from models.users import User
from utils.auth import hash_password

async def seed_users():
    # Ensure schema exists
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        admin_email = "johnny@jjp3.io"
        locksmith_email = "leeno@pkaz.com"
        owner_email = "joel@rsa.com"

        # Check if users exist
        result = await db.execute(select(User).where(User.email.in_([
            admin_email, locksmith_email, owner_email
        ])))
        existing_emails = {user.email for user in result.scalars().all()}

        if admin_email not in existing_emails:
            admin = User(
                email=admin_email,
                hashed_password=hash_password("BAtFitFMA13#*"),
                first_name="Johnny",
                last_name="Wallz",
                role="admin"
            )
            db.add(admin)
            print(f"Created admin user: {admin_email}")

        if locksmith_email not in existing_emails:
            locksmith = User(
                email=locksmith_email,
                hashed_password=hash_password("password"),
                first_name="Abelino",
                last_name="Solis",
                role="locksmith"
            )
            db.add(locksmith)
            print(f"Created locksmith user: {locksmith_email}")

        if owner_email not in existing_emails:
            owner = User(
                email=owner_email,
                hashed_password=hash_password("password"),
                first_name="Joel",
                last_name="Gonzalez",
                role="owner"
            )
            db.add(owner)
            print(f"Created owner user: {owner_email}")

        await db.commit()

async def undo_users():
    async with AsyncSessionLocal() as db:
        await db.execute(text("DELETE FROM users"))
        await db.commit()
        print("🗑️ Deleted all users")

# Optional standalone runner
if __name__ == "__main__":
    asyncio.run(seed_users())