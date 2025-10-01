import json
import aiosqlite
from aiohttp import web

DB_NAME = "advert_website.db"


class AdvertsView(web.View):

    async def get(self):
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT * FROM adverts") as cursor:
                rows = await cursor.fetchall()
                keys = ["id", "title", "description", "created_at", "owner"]
                adverts = [dict(zip(keys, row)) for row in rows]
                return web.json_response(adverts)

    async def post(self):
        try:
            data = await self.request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        if not data.get("title") or not data.get("owner"):
            return web.json_response({"error": "Title and owner are required"}, status=400)
        data = await self.request.json()

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                """
                INSERT INTO adverts (title, description, owner) 
                VALUES (?, ?, ?)
                """, 
                (data["title"], data.get("description"), data["owner"])
            )
            await db.commit()

        return web.json_response({"status": "ok", "message": "Advert created"})


class AdvertView(web.View):
    async def get(self):
        ad_id = self.request.match_info["id"]

        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT * FROM adverts WHERE id = ?", (ad_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    keys = ["id", "title", "description", "created_at", "owner"]
                    return web.json_response(dict(zip(keys, row)))
                return web.json_response({"error": "Advert not found"}, status=404)
    async def patch(self):
        ad_id = self.request.match_info["id"]

        try:
            data = await self.request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        updates = []
        values = []
        for field in ["title", "description", "owner"]:
            if field in data:
                updates.append(f"{field} = ?")
                values.append(data[field])

        if not updates:
            return web.json_response({"error": "No fields to update"}, status=400)

        values.append(ad_id)

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(f"UPDATE adverts SET {', '.join(updates)} WHERE id = ?", tuple(values))
            await db.commit()

        return web.json_response({"status": "ok", "message": f"Advert {ad_id} updated"})
    async def delete(self):
        ad_id = self.request.match_info["id"]

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("DELETE FROM adverts WHERE id = ?", (ad_id,))
            await db.commit()

        return web.json_response({"status": "ok", "message": f"Advert {ad_id} deleted"})


app = web.Application()
app.router.add_get('/adverts', AdvertsView)
app.router.add_post('/adverts', AdvertsView)
app.router.add_get(r'/adverts/{id:\d+}', AdvertView)
app.router.add_patch(r'/adverts/{id:\d+}', AdvertView)
app.router.add_delete(r'/adverts/{id:\d+}', AdvertView)

web.run_app(app)