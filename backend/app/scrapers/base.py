from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.company import Company
from app.models.contact import Contact
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
            usp = company_data.get("usp", ""),
            sector = company_data.get("sector", ""),
            domain_tags = company_data.get("domain_tags", ""),
            headcount_estimate = company_data.get("headcount_estimate", ""),
            funding_round = company_data.get("funding_round", ""),
            status = company_data.get("status", "new"),
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

    def save_contact (self, contact_data:dict)->Contact | None:

        """Saves contacts to the db avoiding duplicates."""

        company_id = contact_data.get("company_id")
        if not company_id:
            return None

        name= contact_data.get("name","no name")
        email = contact_data.get("email","").lower().strip()
        linkedin_url=contact_data.get("linkedin_url","")
        title=contact_data.get("title","")

        existing = self.db.query(Contact).filter(Contact.email == email).first() if email else None
        if existing:
            print(f"Skipping {name} - already exists")
            return existing

        new_contact=Contact(
            company_id=company_id,
            name= name,
            email = email,
            email_verified = contact_data.get("email_verified",False),
            linkedin_url=linkedin_url,
            title=title,
            source=contact_data.get("source")
        )
        
        try:
            self.db.add(new_contact)
            self.db.commit()
            self.db.refresh(new_contact)
            print(f"Saved: {new_contact.name}")
            return new_contact
        except Exception as e:
            self.db.rollback()
            print(f"Error saving contact {new_contact.name}: {e}")
            return None