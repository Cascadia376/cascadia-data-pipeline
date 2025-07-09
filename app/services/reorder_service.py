from ..core.database import db

async def get_reorder_recommendations():
    async with db.pool.acquire() as conn:
        rows = await conn.fetch("SELECT store_id, sku, 10 as recommended_qty FROM inventory WHERE quantity < 5")
        return [dict(row) for row in rows]
