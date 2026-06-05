# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.models.embedding import Embedding

import os
from app.config import settings
os.environ["HF_TOKEN"] = settings.HF_TOKEN


#Load the model once (downloads the 80mb model)
print(f"Loading model all-MiniLM-L6-v2")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded successfully")

def chunk_text(text: str, chunk_size: int = 500)->list[str]:
    """Splits the massive wall of text into smaller chunks"""

    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)

        if len(" ".join(current_chunk))>=chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk= []
        
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def process_and_save_embeddings(db:Session, company_id:int, raw_text:str, source:str="website"):

    """Chunks text, converts to vectors and saves to database"""

    chunks=chunk_text(raw_text)

    for chunk in chunks:
        vector=model.encode(chunk).tolist()
        # id, company_id, chunk_text, source_type, embedding
        embedding=Embedding(
            company_id=company_id,
            chunk_text=chunk,
            source_type=source,
            embedding=vector
        )
        db.add(embedding)
        db.commit()


## testing chuking and encoding

if __name__ == "__main__":
    test_text= "Groww is an Indian financial services company. They help users invest in mutual funds and stocks. Founded in 2016, they have grown rapidly."
    chunks = chunk_text(test_text)
    vector=model.encode(chunks[0]).tolist()
    print(f"Vector of first chunk: {vector}")
    print(f"vector length: {len(vector)}") # should be 384
    print(f"Number of chunks: {len(chunks)}")


    for i, c in enumerate(chunks):
        print(f"Chunk {i} : {c}")
        # for the testing purpose only