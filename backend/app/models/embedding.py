from sqlalchemy import Column, Integer, String, Text, ForeignKey
from pgvector.sqlalchemy import Vector
from app.db.session import Base

class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index = True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    chunk_text = Column(Text, nullable = False)
    source_type = Column(String) # e.g. blog, jd, about, press

    #we use 384 dimensions because we will use the 'all-MiniLM-L6-v2' model.
    # it is efficient and widely used in semantic search.
    embedding=Column(Vector(384), nullable=False)