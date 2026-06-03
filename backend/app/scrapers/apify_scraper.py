# pyrefly: ignore [missing-import]
from apify_client import ApifyClient
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.config import settings
from app.scrapers.base import BaseScraper
import json

def run_apify_scraper(db:Session, actor_id: str = "haketa/ycombinator-companies-scraper",run_input: dict = None):
    print(f"Starting Apify Scraper from {actor_id}")

    #Initialize the ApifyClient with your API token

    client = ApifyClient(settings.APIFY_API_TOKEN)
    base_scraper= BaseScraper(db)

    # If no specific input is provided, we just give it an empty one

    if run_input is None:
        run_input = {}
        print("no input given")

    # Start the actor and wait for it to finish
    run= client.actor(actor_id).call(run_input=run_input)
    print("Scraping finished. Fetching results...")

    #Fetch the results from the actor's default dataset
    dataset_items = client.dataset(run["defaultDatasetId"]).iterate_items()

    saved_count = 0
    for item in dataset_items:
        #Standardise the data format before passing to BaseScraper
        company_data={
            "name": item.get("name") or item.get("companyName"),
            "website": item.get("website") or item.get("url"),
            "description": item.get("description") or item.get("shortDescription", ""),
            "sector":item.get("tags","") or item.get("industry","")
        }
        
        # Only save if we actually found a name and website
        if company_data["name"] and company_data["website"]:
            company = base_scraper.save_company(company_data)
            if company:
                saved_count+=1

    print(f"Apify Scrape Complete: Saved {saved_count} new companies")