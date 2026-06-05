from fastapi import BackgroundTasks, Depends, APIRouter
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.scrapers.apify_scraper import run_apify_scraper
from app.scrapers.pipeline import run_pipeline

router = APIRouter()

@router.post("/run")
def trigger_scraper(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Triggers the Apify scraper as a background task
    """
    #We pass it to background_tasks si the API doesn't freeze while waiting for Apify
    background_tasks.add_task(run_apify_scraper,db)

    return{"status": "ok", "message": "Scraper running in background, Check terminal for logs."}

@router.post("/enrich")
def trigger_pipeline(background_tasks: BackgroundTasks, db:Session = Depends(get_db)):
    background_tasks.add_task(run_pipeline,db)
    return {"status":"ok", "message": "Enrichment pipeline started. Check terminal for logs"}