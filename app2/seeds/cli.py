# app/seeds/cli.py

import asyncio
import typer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from utils.db import engine

# models
from models.users import User


# your existing seed/undo funcs
from seeds import (
    seed_users, undo_users,
)

app = typer.Typer()
Session = async_sessionmaker(engine, expire_on_commit=False)

async def _has_rows(model) -> bool:
    async with Session() as s:
        res = await s.execute(select(model).limit(1))
        return res.scalar_one_or_none() is not None

# === export this for main.py ===
async def seed_all_async():
    if not await _has_rows(User):
        typer.echo("Seeding users…"); await seed_users()
    else:
        typer.echo("Users present — skipping.")

    typer.echo("✅ Seeding complete (idempotent).")

@app.command()
def all():
    asyncio.run(seed_all_async())

@app.command()
def undo():
    asyncio.run(_undo_all())

async def _undo_all():
    typer.echo("Undoing seeded data…")
    await undo_users()
    typer.echo("🗑️ Undo complete!")

if __name__ == "__main__":
    app()