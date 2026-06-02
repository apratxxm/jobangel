from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.db.session import Base

class OutreachLog(Base):
    __tablename__ = "outreach_logs"

    id = Column(Integer, primary_key=True, index = True)
    email_draft_id= Column(Integer, ForeignKey("email_drafts.id", ondelete="CASCADE"), nullable=False)
    
    sent_at = Column(DateTime(timezone=True), server_default = func.now())
    reply_received = Column(Boolean, default=False)
    reply_at=Column(DateTime(timezone=True))
    notes = Column(Text)
