from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SolarFlare(Base):
    __tablename__ = "solar_flares"

    id = Column(Integer, primary_key=True, autoincrement=True)
    flr_id = Column(String(50), unique=True, nullable=False)
    begin_time = Column(DateTime, nullable=False)
    peak_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    class_type = Column(String(5), nullable=False)
    source_location = Column(String(20))
    active_region_num = Column(Integer)
    linked_events = Column(JSON)


