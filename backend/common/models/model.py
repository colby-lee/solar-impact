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


    def to_dict(self):
        """
        Convert SQLAlchemy model instance to dictionary. Useful for FastAPI integration.
        """
        return {
            "id": self.id,
            "flr_id": self.flr_id,
            "begin_time": self.begin_time,
            "peak_time": self.peak_time,
            "end_time": self.end_time,
            "class_type": self.class_type,
            "source_location": self.source_location,
            "active_region_num": self.active_region_num,
            "linked_events": self.linked_events,
        }