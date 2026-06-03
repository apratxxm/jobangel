# JobAngel

> AI-powered personal internship outreach platform that scrapes startups and generates highly personalized cold emails using RAG.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-Postgres-3ECF8E?style=flat-square&logo=supabase)
![Apify](https://img.shields.io/badge/Apify-Scraping-FF6B6B?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-LLaMA3-black?style=flat-square)

## 📖 Introduction
JobAngel automates the most tedious part of applying for tech internships: cold outreach. Instead of manually searching for companies and writing repetitive emails, JobAngel scrapes startup directories, saves the data to a local-first database, and uses the Groq LLM to write highly personalized cold emails based on your specific profile. 

## 🛠️ Technologies Used
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL via Supabase (Free Tier)
- **ORM & Migrations:** SQLAlchemy 2.0 & Alembic
- **Vector Search:** `pgvector` for Retrieval-Augmented Generation (RAG)
- **Scraping:** Apify Python Client
- **AI/LLM:** Groq API (LLaMA 3.1 70B)
- **Email Delivery:** Python `smtplib` (Gmail SMTP)

## ✨ Features
- **Automated Startup Scraping:** Trigger Apify actors to pull structured data from startup directories (like YCombinator).
- **Smart Deduplication:** Automatically normalizes domain names to prevent saving duplicate companies.
- **RAG-Powered Personalization:** Stores scraped company data in vector embeddings so the LLM knows exactly what the company builds before writing the email.
- **Outbox Management:** Generate, review, edit, and approve emails locally before they are actually sent.

## 🏗️ Process of Building It
1. **Database Schema:** Designed a robust SQLAlchemy schema with tables for `Companies`, `Contacts`, `EmailDrafts`, `OutreachLogs`, and `Embeddings`.
2. **Migrations:** Configured Alembic to connect to a Supabase IPv4 transaction pooler to manage schema migrations.
3. **Base Scraper Logic:** Built a foundational scraping class that handles data normalization and duplicate prevention.
4. **Third-Party Integrations:** Hooked into Apify for reliable data extraction without dealing with manual HTML parsing and Captchas.
5. **API Layer:** Wrapped the functionality in a lightning-fast FastAPI server.

## 🧠 What I Learned
- Managing database migrations with **Alembic** and troubleshooting connection pooler issues (IPv4 vs IPv6) on Supabase.
- Using Python's **Pydantic** for strict environment variable validation.
- Abstracting web scraping complexities by leveraging **Apify Actors**.
- Designing a local-first application architecture that integrates powerful cloud tools (Supabase, Groq) while maintaining zero deployment costs.

## 🚀 How It Can Be Improved
- **Frontend Dashboard:** Build the planned Next.js dashboard to visually manage scraped companies and edit emails.
- **Gmail API Integration:** Upgrade from standard SMTP to the official Gmail API for better deliverability tracking.
- **Automated Scheduling:** Implement background tasks (like Celery or FastAPI BackgroundTasks) to run scrapers automatically every week.
- **Deeper Enrichment:** Add a module to automatically search GitHub or LinkedIn for the startup founders' direct email addresses.

## 💻 How to Run the Project

1. **Clone & Setup Environment**
   ```bash
   git clone <your-repo-url>
   cd jobangel
   python -m venv venv
   venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

2. **Configure Secrets**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_key
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your_gmail_app_password
   APIFY_API_TOKEN=your_apify_token
   DATABASE_URL=postgresql://postgres:[password]@aws-0-region.pooler.supabase.com:5432/postgres
   ```

3. **Run Database Migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Start the Server**
   ```bash
   uvicorn app.main:app --reload
   ```
   *Visit `http://localhost:8000/docs` to see the API dashboard.*
