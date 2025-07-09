from ..core.database import db

async def get_sales_summary():
    async with db.pool.acquire() as conn:
        rows = await conn.fetch("SELECT store_id, SUM(price*quantity) as total_sales, SUM(quantity) as total_units FROM sales GROUP BY store_id")
        return [dict(row) for row in rows]

async def get_inventory_status():
    async with db.pool.acquire() as conn:
        rows = await conn.fetch("SELECT store_id, sku, quantity FROM inventory")
        return [dict(row) for row in rows]
