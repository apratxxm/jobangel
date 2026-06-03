from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.embedding import Embedding
from app.scrapers.enricher import scrape_website_text
from app.scrapers.embedder import chunk_text, process_and_save_embeddings

def run_pipeline(db:Session):
    """Runs the complete scrapign and embedding pipeline"""
    companies=db.query(Company).all()

    for company in companies:
        already_done= db.query(Embedding).filter(Embedding.company_id == company.id).first()

        if already_done:
            print(f"Already processed {company.name}. Skipping")
            continue

        print(f"Processing company:{company.name}")
        website_text= scrape_website_text(company.website)

        if website_text:
            process_and_save_embeddings(db=db, company_id=company.id, raw_text=website_text)
            print(f"embedding done {company.name}")
        else:
            print(f"Could not scrape {company.name}")
        
    print("Pipeline Run Complete")
