from fastapi import APIRouter, Depends
from ..models import schemas
from ..services import ingestion_service, dashboard_service, reorder_service
from ..utils.dependencies import verify_write_allowed

router = APIRouter()

@router.get("/dashboard/sales-summary", response_model=list[schemas.SalesSummary])
async def sales_summary():
    data = await dashboard_service.get_sales_summary()
    return [schemas.SalesSummary(**row) for row in data]

@router.get("/dashboard/inventory-status", response_model=list[schemas.InventoryStatus])
async def inventory_status():
    data = await dashboard_service.get_inventory_status()
    return [schemas.InventoryStatus(**row) for row in data]

@router.post("/ingest/sales")
async def ingest_sales(payload: schemas.SalesIngestion, allowed: bool = Depends(verify_write_allowed)):
    await ingestion_service.insert_sales(payload.records)
    return {"status": "success", "ingested": len(payload.records)}

@router.post("/ingest/inventory")
async def ingest_inventory(payload: schemas.InventoryIngestion, allowed: bool = Depends(verify_write_allowed)):
    await ingestion_service.insert_inventory(payload.records)
    return {"status": "success", "ingested": len(payload.records)}

@router.get("/reorder/recommendations", response_model=list[schemas.ReorderRecommendation])
async def reorder_recommendations():
    data = await reorder_service.get_reorder_recommendations()
    return [schemas.ReorderRecommendation(**row) for row in data]

api_router = router
