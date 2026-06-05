from apify_client import ApifyClient
from sqlalchemy.orm import Session
from app.config import settings
from app.scrapers.base import BaseScraper
import time

def run_apify_scraper(db:Session, actor_id: str = "fatihtahta/y-combinator-directory-scraper",run_input: dict = None):
    print(f"Starting Apify Scraper from {actor_id}")

    #Initialize the ApifyClient with your API token
    client = ApifyClient(settings.APIFY_API_TOKEN)
    base_scraper= BaseScraper(db)

    # If no specific input is provided, we just give it an empty one
    if run_input is None:
        run_input = {
            "get_founders": True,
            "getEmails": True,
            "includeRiskyEmails": True,
            "isHiring": True,
            "nonprofit": False,
            "batches": ["Spring 2026", "Winter 2026", "Fall 2025", "Summer 2025"],
            "regions": ["America / Canada", "Remote", "South Asia"],
            "queries": ["machine learning","LLM","natural language processing","developer tools","MLOps","agentic AI",
            "AI infrastructure"],
            "maxEmployeeSize": "100",
            "limit": 25
        }
        print(f"run_input updated to {run_input}")

    run=None

    for attempt in range(3):
        try:
            print(f"Apify Run attempt {attempt+1}")
            run = client.actor(actor_id).call(run_input=run_input)
            print("Scraping finished. Fetching results...")
            break
        except Exception as e:
            print(f"Run attempt {attempt+1} failed: {e}")
            if attempt <2:
                time.sleep(5)

    if not run:
        print(f"All three scraping attempts failed. Exiting.")
        return

    saved_count=0
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():

        details=item.get("company_details",{})
        tags = details.get("tags", [])

        company_data={
            "name": item.get("name"),
            "website": item.get("website"),
            "description": item.get("description") or item.get("one_liner", ""),
            "usp": item.get("one_liner", ""),
            "sector": details.get("industry", ""),
            "domain_tags": ", ".join(tags) if tags else "",
            "headcount_estimate": str(details.get("team_size") or ""),
            "funding_round": details.get("stage", ""),
            "status": "hiring" if item.get("is_hiring") else "new",
        }

        if not company_data["website"]:
            company_data["website"]=item.get("url","")
            print(f"No website for {company_data['name']}, using YC profle URL as a fallback")

        if not company_data["name"]:
            print(f"Skipping, no company name found in record")
            continue

        company=base_scraper.save_company(company_data)

        if company:
            saved_count+=1
            #save each founder as a contact
            for founder in item.get("founders", []):
                name = founder.get("name", "")
                if not name:
                    continue  # skip only if we don't even have a name
    
                contact_data = {
                    "company_id": company.id,
                    "name": name,
                    "email": founder.get("email", ""),
                    "email_verified": founder.get("email_status") == "verified",
                    "linkedin_url": founder.get("linkedin_url", ""),
                    "title": founder.get("title", ""),
                    "source": "apify_yc",
                }
                base_scraper.save_contact(contact_data)

    print(f"Apify Scrape Complete: Saved {saved_count} new companies")