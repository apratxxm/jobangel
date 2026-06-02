from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.session import Base

class Contact(Base):
    __tablename__ = "contacts"

    id= Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    title = Column(String)
    email = Column(String, nullable=False)
    linkedin_url = Column(String)
    confidence = Column(String) # high/ medium/ low
    source = Column(String) # hunter/ pattern/ manual

    