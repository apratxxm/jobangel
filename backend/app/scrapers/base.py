# base scraper class
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.company import Company
import urllib.parse

class BaseScraper:
    def __init__(self, db:Session):
        self.db = db

    def normalize_domain(self, url:str)-> str:
        """ Strips http://, www., and paths from a URL to get just the domain. """
        if not url:
            return ""
        parsed = urllib.parse.urlparse(url if "//" in url else f"http://{url}")
        domain = parsed.netloc.lower()
        if domain.startswith("www"):
            domain = domain[4:]
        return domain

    def save_company(self, company_data: dict)->Company | None:
        """ Saves a company to the DB, avoiding duplicates based on normalized domain. """
        website = company_data.get("website", "")
        domain = self.normalize_domain(website)

        if not domain:
            print(f"Skipping {company_data.get('name')} - no website provided")
            return None
        
        # checking for duplicates
        existing = self.db.query(Company).filter(Company.normalized_domain == domain).first()
        if existing:
            print(f"Skipping {company_data.get('name')} - already exists as {existing.name} with domain {domain}")
            return existing
        
        new_company = Company(
            name = company_data.get("name"),
            website = website,
            normalized_domain = domain,
            description = company_data.get("description", ""),
            sector = company_data.get("sector", "")
        )
        try:
            self.db.add(new_company)
            self.db.commit()
            self.db.refresh(new_company)
            print(f"Saved: {new_company.name} | {new_company.website}")
            return new_company
        except IntegrityError:
            self.db.rollback()
            print(f"Integrity error saving company: {new_company.name}")
            return None
        except Exception as e:
            self.db.rollback()
            print(f"Error saving company {new_company.name}: {e}")
            return None