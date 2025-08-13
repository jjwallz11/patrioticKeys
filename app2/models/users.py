# app/models/users.py

from sqlalchemy import Column, Integer, String, CheckConstraint
from utils.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)  # Optional for company owners, required for admins
    last_name = Column(String, nullable=True)   # Optional for company owners, required for admins
    company = Column(String, nullable=True)     # Optional field for company name
    phone = Column(String, nullable=True)       # Optional field for phone
    role = Column(String, default="owner", nullable=False)  # 'owner', 'admin', etc.
    aks_api_key = Column(String, nullable=True) 
    
    __table_args__ = (
        CheckConstraint(
            "role != 'admin' OR (first_name IS NOT NULL AND last_name IS NOT NULL)",
            name="admin_name_required"
        ),
    )
    