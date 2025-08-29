from typing import Union, Optional, Dict
from collections import Counter

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from common.db import DatabaseManager
from common.models.model import SolarFlare


router = APIRouter()

@router.get("/peak-frequency")
def get_peak_frequency(start_date: str, end_date: str):
    """
    Analyze solar flares to find the most common class within a date range.
    """
    with DatabaseManager.session_scope() as session:
        solar_flares = (
            session.query(SolarFlare)
            .filter(SolarFlare.begin_time >= start_date, SolarFlare.end_time <= end_date)
            .all()
        )

        # Calculate frequencies
        frequencies = {}
        for flare in solar_flares:
            class_type = flare.class_type
            if class_type in frequencies:
                frequencies[class_type] += 1
            else:
                frequencies[class_type] = 1

        # Find the most common class
        most_common_class = max(frequencies, key=frequencies.get) if frequencies else None

        # Prepare response
        response = {
            "start_date": start_date,
            "end_date": end_date,
            "most_common_class": most_common_class,
            "peak_frequencies": frequencies,
        }
        return response

@router.get("/activity-summary")
def get_activity_summary(start_date: str, end_date: str):
    """
    Summarize solar flare activity within a date range.
    """
    with DatabaseManager.session_scope() as session:
        flares = session.query(SolarFlare).filter(
            SolarFlare.begin_time >= start_date,
            SolarFlare.begin_time <= end_date
        ).all()

        # Calculate peak intensity and counts
        intensities = [flare.class_type for flare in flares if flare.class_type]
        intensity_counts = Counter(intensities)
        peak_intensity_class = (
            max(intensities, key=intensity_counts.get) if intensities else "No data"
        )

        # Prepare response
        response = {
            "start_date": start_date,
            "end_date": end_date,
            "total_flares": len(flares),
            "peak_intensity_class": peak_intensity_class,  # Always a string
            "intensity_counts": dict(intensity_counts),
        }
        return response


@router.get("/longest-flare", response_model=Dict[str, Union[str, float]])
def get_longest_solar_flare(start_date: str, end_date: str):
    """
    Find the longest-duration solar flare within a date range.
    """
    with DatabaseManager.session_scope() as session:
        solar_flares = (
            session.query(SolarFlare)
            .filter(SolarFlare.begin_time >= start_date, SolarFlare.end_time <= end_date)
            .all()
        )
        if not solar_flares:
            raise HTTPException(status_code=404, detail="No solar flares found in the specified date range")

        longest_flare = max(
            solar_flares,
            key=lambda flare: (flare.end_time - flare.begin_time).total_seconds()
            if flare.end_time and flare.begin_time
            else 0,
        )

        duration = (longest_flare.end_time - longest_flare.begin_time).total_seconds()
        return {
            "flr_id": longest_flare.flr_id,
            "duration_seconds": duration,
            "class_type": longest_flare.class_type,
        }