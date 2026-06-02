# JobAngel — Project Architecture

## What this is
A personal internship outreach platform. It scrapes recently-funded Indian startups and ML-focused companies, enriches each one with context, filters by relevance to your profile, uses an LLM to generate short personalized cold emails, and gives you a dashboard to review, edit, and send them.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | Next.js 14 (App Router) | Full-stack capable, fast, great DX |
| Backend | FastAPI (Python) | Async, typed, perfect for scraping + LLM work |
| ORM | SQLAlchemy 2.0 + Alembic | Clean models, schema migrations via Alembic |
| Database | Supabase (managed Postgres + pgvector) | Free tier, pgvector built-in, no Docker needed |
| Vector Search | pgvector (via Supabase) | Postgres extension for RAG — no separate vector DB |
| Scraping | Playwright + BeautifulSoup + httpx | Handles JS-heavy pages + static pages |
| Task Queue | FastAPI BackgroundTasks | Scraping runs async in the background; no Celery or Redis needed |
| LLM | Groq API (LLaMA 3.1 70B) | Free tier, fast, no credit card |
| Email Send | Gmail SMTP (via `smtplib`) | 100% free, no domain setup, runs locally via App Passwords |
| Styling | Tailwind CSS + shadcn/ui | Fast, consistent, looks good |

---

## Deployment Strategy

**Local-first**
- FastAPI runs on `localhost:8000`
- Next.js runs on `localhost:3000`
- Supabase is already cloud — no local DB setup needed
- No Docker required
- Everything runs locally for zero cost, eliminating cold-start and deployment complexity.

---

## Project Directory Structure

```
jobangel/
│
├── frontend/                          # Next.js 14
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                   # Dashboard home / stats
│   │   ├── companies/
│   │   │   ├── page.tsx               # Company list + filters
│   │   │   └── [id]/
│   │   │       └── page.tsx           # Company detail + email editor
│   │   ├── outbox/
│   │   │   └── page.tsx               # Approved emails, send queue
│   │   ├── settings/
│   │   │   └── page.tsx               # Email config (Gmail SMTP), Groq key, profile
│   │   └── api/                       # Next.js API routes (proxy to FastAPI)
│   │       └── proxy/[...path]/
│   │           └── route.ts           
│   ├── components/
│   │   ├── CompanyCard.tsx
│   │   ├── EmailEditor.tsx
│   │   ├── RelevanceScore.tsx
│   │   ├── StatusBadge.tsx
│   │   └── Sidebar.tsx
│   ├── lib/
│   │   ├── api.ts                     # Typed fetch wrappers to FastAPI
│   │   └── types.ts                   # Shared TypeScript types
│   ├── public/
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── backend/                           # FastAPI
│   ├── app/
│   │   ├── main.py                    # FastAPI app init, CORS, router mount
│   │   ├── config.py                  # Settings via pydantic-settings (.env)
│   │   │
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── company.py             # Company
│   │   │   ├── contact.py             # Contact (founder/HR email)
│   │   │   ├── email_draft.py         # EmailDraft (generated + edited)
│   │   │   ├── outreach.py            # OutreachLog (sent, replied, etc.)
│   │   │   └── embedding.py           # Embedding (pgvector, for RAG)
│   │   │
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   │   ├── company.py
│   │   │   ├── contact.py
│   │   │   └── email_draft.py
│   │   │
│   │   ├── routers/                   # API route handlers
│   │   │   ├── companies.py           # GET /companies, GET /companies/{id}
│   │   │   ├── scrape.py              # POST /scrape/run (kicks off BackgroundTask)
│   │   │   ├── enrich.py              # POST /enrich/{company_id}
│   │   │   ├── emails.py              # POST /emails/generate, PATCH /emails/{id}
│   │   │   ├── outbox.py              # POST /outbox/send, GET /outbox
│   │   │   └── settings.py            # GET/POST /settings
│   │   │
│   │   ├── scrapers/                  # One file per source
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Abstract base scraper class
│   │   │   ├── crunchbase.py          # Crunchbase funded companies
│   │   │   ├── ycombinator.py         # YC batch pages
│   │   │   ├── linkedin_jobs.py       # LinkedIn job listings (careful)
│   │   │   ├── naukri.py              # Naukri ML/AI job listings
│   │   │   ├── inc42.py               # Inc42 startup news
│   │   │   └── careers_page.py        # Company careers page direct scrape
│   │   │
│   │   ├── enrichment/
│   │   │   ├── __init__.py
│   │   │   ├── company_summary.py     # Summarize what they do (from site/blog)
│   │   │   ├── contact_finder.py      # WHOIS, GitHub, Search Dorks, Mailto scraping, pattern guessing
│   │   │   ├── relevance_scorer.py    # Score company against your profile
│   │   │   └── news_hook.py           # Pull recent tweet / press release as hook
│   │   │
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py              # Chunk + embed company docs into pgvector
│   │   │   └── retriever.py           # Query pgvector for relevant context
│   │   │
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── client.py              # Groq API client wrapper
│   │   │   ├── prompt_builder.py      # Builds prompt from company card + RAG context
│   │   │   └── email_generator.py     # Calls LLM, returns subject + body
│   │   │
│   │   ├── email/
│   │   │   ├── __init__.py
│   │   │   ├── sender.py              # Gmail SMTP send logic (smtplib)
│   │   │   └── templates.py           # Fallback plain-text template
│   │   │
│   │   ├── tasks/                     # Scraping + enrichment runners
│   │   │   ├── __init__.py
│   │   │   ├── scrape_runner.py       # run_full_scrape(), run_source_scrape()
│   │   │   └── enrich_runner.py       # enrich_company(), batch_enrich()
│   │   │
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── session.py             # SQLAlchemy engine + SessionLocal
│   │       └── init_db.py             # create_all() for dev
│   │
│   ├── migrations/                    # Alembic
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │
│   ├── tests/
│   ├── .env.example
│   ├── requirements.txt
│   └── pyproject.toml
│
├── .env                               # Shared secrets
└── README.md
```

---

## Data Flow (end to end)

```
[Scraper runs — asynchronously via FastAPI BackgroundTasks]
    → raw company data saved to DB (Company table)
    → duplicates detected by normalized_domain (e.g. 'acme.com'), skipped or merged

[Enrichment runs per company]
    → company blog/JD text scraped, chunked, and embedded into pgvector
    → contact_finder resolves founder email via WHOIS, GitHub, Search Dorks, or Mailto scraping
    → news_hook pulls latest tweet or press hit
    → relevance_scorer tags and scores the company
    → company card fully populated in DB

[LLM Email Generation]
    → retriever pulls top-k relevant chunks from pgvector for that company
    → prompt_builder assembles: company card + RAG context + your profile
    → Groq LLM generates subject + body (max 120 words)
    → EmailDraft saved to DB, status = "draft"

[Dashboard]
    → You see ranked company list
    → Click into company → see enrichment card + generated email
    → Edit email in-place → save → approve
    → Approved emails go to outbox

[Outbox / Send]
    → You trigger send per email or batch
    → Sent via Gmail SMTP (using secure ssl/tls connection via smtplib)
    → OutreachLog created (sent_at, to, subject)
    → Status updates: sent → replied → rejected (you update manually)
```

---

## Database Schema (SQLAlchemy models)

```
Company
  id, name, website, normalized_domain, domain_tags, sector,
  funding_amount, funding_round, funding_date,
  headcount_estimate, description, usp,
  relevance_score, status, created_at
  UNIQUE(normalized_domain)            # deduplication constraint

Contact
  id, company_id (FK), name, title,
  email, linkedin_url, confidence (high/medium/guessed),
  source (hunter/pattern/manual)

EmailDraft
  id, company_id (FK), contact_id (FK),
  subject, body, status (draft/approved/sent),
  generated_at, edited_at, sent_at

OutreachLog
  id, email_draft_id (FK), sent_at,
  reply_received (bool), reply_at, notes

Embedding
  id, company_id (FK), chunk_text, source_type (blog/jd/about/press),
  embedding (Vector(384))              # pgvector column
```

---

## Email Configuration (Gmail SMTP)

Instead of setting up commercial email delivery services like AWS SES, this project uses standard **Gmail SMTP**. It allows sending directly from your personal Gmail address for local testing and cold emailing at a small scale.

### How it works:
1. **Gmail App Password:** You do not use your primary Google account password. Instead, generate a 16-character **App Password** from your Google Account Security settings (requires 2-Step Verification enabled).
2. **Library:** Python's built-in `smtplib` and `email.mime` modules handle the SMTP handshake and format the MIME messages.
3. **Port:** Port `587` with STARTTLS ensures the credentials and email contents are encrypted in transit.

### Limitations:
- Gmail limits free accounts to approximately **500 emails per day**.
- Emails will land in the primary inbox of recipients if personalized well, but sending spammy patterns or excessive volume will trigger Gmail's outbound spam filters.

---

## Where RAG fits

The problem RAG solves here: the LLM needs *rich, specific* context about each company to write a genuinely personalized email — not just a 2-line description. But you can't stuff an entire company blog into a prompt.

**What gets embedded (stored in Supabase via pgvector):**
- Company blog posts / product announcements (last 3)
- Job description text for roles that match your profile
- About page / founder interview text
- Any press coverage pulled from news_hook

**At generation time:**
- Query pgvector with something like *"NLP internship BERT fine-tuning {company_name}"*
- Get top 3-5 chunks back via cosine similarity (`<=>` operator)
- Those chunks go into the prompt as grounding context
- LLM writes a more specific email because it actually knows what the company is working on

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2` — runs locally, free, fast, no API needed.
**No separate vector database needed** — pgvector is already enabled on all Supabase projects. One less service to manage.

---

## Environment Variables (`.env`)

```
# LLM
GROQ_API_KEY=

# Email (Gmail SMTP Setup)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password  # 16-character Google App Password

# Optional
SERP_API_KEY=          # for news/search enrichment

# Supabase (Postgres + pgvector)
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

---

## Cost Breakdown

| Service | Phase 1 (local) | Phase 2 (Vercel) |
|---|---|---|
| Frontend | localhost (free) | Vercel (free) |
| Supabase (Postgres + pgvector) | Free (500MB) | Free (500MB) |
| Groq (LLM) | Free | Free |
| Email Send | Gmail SMTP (free, ~500/day limit) | Same |
| Embeddings | sentence-transformers (free, local) | Supabase embeddings or pre-computed |
| Contact Finder | Free (WHOIS, GitHub, Google Dorks, Mailto scraping) | Same |
| **Total** | **$0** | **$0** |

---

## Build Order

1. **Backend skeleton** — FastAPI app, SQLAlchemy models, Alembic migrations, DB session
2. **One scraper** — start with Inc42 or YC batch (simplest, no login wall)
3. **Enrichment basics** — company summary + contact finder
4. **LLM generation** — Groq client + prompt builder (no RAG yet)
5. **Frontend scaffold** — Next.js, company list page, company detail + email editor
6. **Wire frontend ↔ backend** — full flow working end to end
7. **Add RAG** — pgvector, embed JDs + blog posts into Supabase, improve email quality
8. **Add email sending** — Gmail SMTP (smtplib)
