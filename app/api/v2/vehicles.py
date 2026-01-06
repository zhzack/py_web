from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from models.vehicle import VehicleModel
from schemas.vehicle import VehicleOut

router = APIRouter()

@router.get("/", response_model=List[VehicleOut])
def list_vehicles(
    chip: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(VehicleModel)
    if chip:
        query = query.filter(VehicleModel.chip_platform == chip)
    return query.all()