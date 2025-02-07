from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from common.db import DatabaseManager
from common.models.model import SolarFlare

router = APIRouter()

@router.get("/solar-flares", response_model=List[dict])
def get_solar_flares(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DDTHH:MM:SS format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DDTHH:MM:SS format")
):
    """
    Fetch solar flares from the database, optionally filtering by date range.
    """
    with DatabaseManager.session_scope() as session:
        query = session.query(SolarFlare)

        # Apply date filters if provided
        if start_date:
            query = query.filter(SolarFlare.begin_time >= start_date)
        if end_date:
            query = query.filter(SolarFlare.end_time <= end_date)

        solar_flares = query.all()
        return [flare.to_dict() for flare in solar_flares]

@router.get("/solar-flares/{flr_id}", response_model=dict)
def get_solar_flare(flr_id: str):
    """
    Fetch a single solar flare by its unique ID.
    """
    with DatabaseManager.session_scope() as session:
        solar_flare = session.query(SolarFlare).filter_by(flr_id=flr_id).first()
        if not solar_flare:
            raise HTTPException(status_code=404, detail="Solar flare not found")
        return solar_flare.to_dict()