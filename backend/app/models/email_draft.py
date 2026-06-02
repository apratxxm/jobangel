from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id=Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    contact_id= Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"))

    subject= Column(String)
    body= Column(Text)
    status = Column (String, default="draft") # draft/ approved/ sent

    generated_at = Column(DateTime(timezone=True), server_default = func.now())
    edited_at = Column(DateTime(timezone=True), onupdate=func.now())
    sent_at = Column(DateTime(timezone=True))
    