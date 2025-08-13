# app/models/vehicles.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from utils.db import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vin = Column(String(17), unique=True, index=True, nullable=False)
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    body_type = Column(String(100), nullable=True)
    fuel_type = Column(String(100), nullable=True)
    manufacturer = Column(String(255), nullable=True)
    plant_country = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", backref="vehicles")