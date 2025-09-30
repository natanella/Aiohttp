import aiosqlite
import asyncio

async def migrate():
    async with aiosqlite.connect("advert_website.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS adverts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            owner TEXT NOT NULL
        )
        """)
        await db.commit()
    print("Миграция выполнена — база данных создана!")

asyncio.run(migrate())