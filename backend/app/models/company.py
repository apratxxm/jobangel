from sqlalchemy import Column, Integer, String, Float , DateTime, Text
from sqlalchemy.sql import func
from app.db.session import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    website = Column(String, nullable=True)
    normalized_domain = Column(String, unique=True, index=True, nullable=False)
    domain_tags= Column(String)
    sector= Column(String)
    
    funding_amount = Column(String)
    funding_round = Column(String)
    funding_date = Column(String)

    headcount_estimate= Column(String)
    description = Column(Text)
    usp= Column(Text)

    relevance_score = Column(Float)
    status = Column(String, default="new") # new/ enriched/ emailed/ skipped

    created_at = Column(DateTime(timezone=True), server_default = func.now())
    
