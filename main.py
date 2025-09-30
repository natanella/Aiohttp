import aiosqlite
from aiohttp import web


class AdvertsView(web.View):
    DB_NAME = "advert_website.db"

    async def get(self):
        async with aiosqlite.connect(self.DB_NAME) as db:
            async with db.execute("SELECT * FROM adverts") as cursor:
                rows = await cursor.fetchall()
                keys = ["id", "title", "description", "created_at", "owner"]
                adverts = [dict(zip(keys, row)) for row in rows]
                return web.json_response(adverts)

    async def post(self):
        data = await self.request.json()

        async with aiosqlite.connect(self.DB_NAME) as db:
            await db.execute(
                """
                INSERT INTO adverts (title, description, owner) 
                VALUES (?, ?, ?)
                """, 
                (data["title"], data.get("description"), data["owner"])
            )
            await db.commit()

        return web.json_response({"status": "ok", "message": "Advert created"})

    async def patch(self):
        data = await self.request.json()
        ad_id = data.get("id")
        if not ad_id:
            return web.json_response({"error": "Missing id"}, status=400)

        async with aiosqlite.connect(self.DB_NAME) as db:
            updates = []
            values = []

            for field in ["title", "description", "owner"]:
                if field in data:
                    updates.append(f"{field} = ?")
                    values.append(data[field])

            if not updates:
                return web.json_response({"error": "No fields to update"}, status=400)

            values.append(ad_id)
            query = f"UPDATE adverts SET {', '.join(updates)} WHERE id = ?"
            await db.execute(query, tuple(values))
            await db.commit()

        return web.json_response({"status": "ok", "message": f"Advert {ad_id} updated"})



    async def delete(self):
        data = await self.request.json()

        ad_id = data.get("id")
        if not ad_id:
            return web.json_response({"error": "Missing id"}, status=400)

        async with aiosqlite.connect(self.DB_NAME) as db:
            await db.execute("DELETE FROM adverts WHERE id = ?", (ad_id,))
            await db.commit()

        return web.json_response({"status": "ok", "message": f"Advert {ad_id} deleted"})



app = web.Application()
app.router.add_route('*', '/adverts', AdvertsView)

web.run_app(app)