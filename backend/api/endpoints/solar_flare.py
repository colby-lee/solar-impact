import json
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Query, Depends

from common.db import DatabaseManager
from common.models.model import SolarFlare
from common.utils import send_rabbitmq_message


class DataCollectionRequest(BaseModel):
    start_date: datetime
    end_date: datetime


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

 
@router.post("/start-data-collection")
def start_data_collection(request: DataCollectionRequest):
    """
    Start data collection by sending a message to RabbitMQ.
    """
    try:
        # Convert datetime objects to string in ISO 8601 format
        start_date_str = request.start_date.isoformat()
        end_date_str = request.end_date.isoformat()

        # Prepare the message to be sent to RabbitMQ
        message = {"start_date": start_date_str, "end_date": end_date_str}
        
        # Send the message to RabbitMQ 
        send_rabbitmq_message("data_collection_queue", message)

        return {"status": "Data collection triggered successfully", "message": message}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger data collection: {e}")
    
# @router.get("/solar-flares-debug", response_model=List[dict])
# def debug_get_all_flares(db: Session = Depends(get_db)):
#     flares = db.query(SolarFlare).all()
#     return [flare.to_dict() for flare in flares]