from datetime import date
from typing import List
from pydantic import BaseModel, validator, constr, condecimal, PositiveInt

SkuStr = constr(regex=r"^[A-Za-z0-9_-]{1,20}$")

class SalesRecord(BaseModel):
    store_id: int
    sku: SkuStr
    quantity: PositiveInt
    price: condecimal(gt=0)
    sale_date: date

    @validator("sale_date")
    def not_future(cls, v: date):
        if v > date.today():
            raise ValueError("sale_date cannot be in the future")
        return v

class InventoryRecord(BaseModel):
    store_id: int
    sku: SkuStr
    quantity: PositiveInt
    last_updated: date

    @validator("last_updated")
    def not_future(cls, v: date):
        if v > date.today():
            raise ValueError("last_updated cannot be in the future")
        return v

class SalesIngestion(BaseModel):
    records: List[SalesRecord]

class InventoryIngestion(BaseModel):
    records: List[InventoryRecord]

class SalesSummary(BaseModel):
    store_id: int
    total_sales: float
    total_units: int

class InventoryStatus(BaseModel):
    store_id: int
    sku: SkuStr
    quantity: int

class ReorderRecommendation(BaseModel):
    sku: SkuStr
    store_id: int
    recommended_qty: int
