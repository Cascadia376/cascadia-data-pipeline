from ..core.database import db
from ..models.schemas import SalesRecord, InventoryRecord
from ..services.audit import log_change

async def insert_sales(records):
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            for record in records:
                await conn.execute(
                    "INSERT INTO sales (store_id, sku, quantity, price, sale_date) VALUES ($1, $2, $3, $4, $5)",
                    record.store_id,
                    record.sku,
                    record.quantity,
                    record.price,
                    record.sale_date,
                )
            await log_change("insert_sales", {"count": len(records)})

async def insert_inventory(records):
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            for record in records:
                await conn.execute(
                    "INSERT INTO inventory (store_id, sku, quantity, last_updated) VALUES ($1, $2, $3, $4)",
                    record.store_id,
                    record.sku,
                    record.quantity,
                    record.last_updated,
                )
            await log_change("insert_inventory", {"count": len(records)})
