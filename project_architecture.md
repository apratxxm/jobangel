# JobAngel — Project Architecture (Living Document)

> Last updated: June 2026. This document reflects actual decisions made during implementation, not just the original plan. Sections marked **[PIVOT]** show where we deviated from the original plan and why.

---

## What this is

A personal internship outreach platform. It scrapes recently-funded Indian startups and ML-focused companies, enriches each one with context, filters by relevance to your profile, uses an LLM to generate short personalized cold emails, and gives you a dashboard to review, edit, and send them.

---

## Tech Stack (Actual)

| Layer | Technology | Why |
|---|---|---|
| Frontend | Next.js 14 (App Router) | Full-stack capable, fast, great DX |
| Backend | FastAPI (Python) | Async, typed, perfect for scraping + LLM work |
| ORM | SQLAlchemy 2.0 + Alembic | Clean models, schema migrations via Alembic |
| Database | Supabase (managed Postgres + pgvector) | Free tier, pgvector built-in, no Docker needed |
| Vector Search | pgvector (via Supabase) | Postgres extension for RAG — no separate vector DB |
| Scraping | Apify (`fatihtahta/y-combinator-directory-scraper`) | **[PIVOT]** See scraper decisions below |
| Website text | `requests` + `BeautifulSoup` | Static scraping for homepage text (enricher.py) |
| Embedding | `sentence-transformers/all-MiniLM-L6-v2` | Runs locally, free, 384-dim vectors |
| Task Queue | FastAPI BackgroundTasks | Scraping runs async — no Celery or Redis needed |
| LLM | Groq API (llama-3.1-8b-instant) | Free tier, fast, 131K context window |
| Email Send | Gmail SMTP (via `smtplib`) | 100% free, ~500 emails/day limit |
| Frontend | Next.js 14 (App Router) | **[NOT STARTED]** |

---

## Deployment Strategy

**Phase 1 — Local**
- FastAPI runs on `localhost:8000`
- Next.js runs on `localhost:3000`
- Supabase is already cloud — no local DB setup needed
- No Docker required

**Phase 2 — Deployed**
- Frontend: Vercel (free tier, connects to GitHub)
- Backend: Railway or Render (free tier for FastAPI)
- DB: Supabase stays as-is (already cloud)
- Scraping/embedding still triggered manually via API or a scheduled Apify run

---

## Scraper Decisions [PIVOT]

### Original Plan
Use Playwright + BeautifulSoup + httpx across multiple sources: Crunchbase, YC batch pages, LinkedIn, Naukri, Inc42.

### What We Actually Did (Phase 1)
**Replaced individual scrapers with Apify**, accepting it as an external dependency. YC is the first source — not the only one.

### Planned Future Data Sources
| Source | What it gives | Tool |
|---|---|---|
| YC directory | 5900+ funded startups, founder emails, job descriptions | Apify fatihtahta ✅ (current) |
| Indian startups (Inc42, YourStory) | Recently funded Indian companies | Apify actor or custom BS4 scraper |
| LinkedIn Jobs | ML/AI job postings at startups | Apify (careful — ToS) |
| Naukri / Instahyre | Indian ML job listings | Apify or requests + BS4 |
| Crunchbase | Funding rounds, investor data | Apify |

Each new source feeds the same `BaseScraper.save_company()` + `save_contact()` pipeline — the base class handles deduplication regardless of source.

#### Scraper Evaluation (all four options considered):

| Actor | Price | Emails | Jobs | Reliability | Decision |
|---|---|---|---|---|---|
| `haketa/ycombinator-companies-scraper` | Free | ✗ | ✗ | ~98% | Started here, then pivoted |
| `michael.g/y-combinator-scraper` | $150/1k | ✓ verified | ✓ | >99% | Too expensive |
| `clearpath/ycombinator-api-scraper` | $3.50/1k | ✗ | ✓ | >99% | Good but no emails |
| `fatihtahta/y-combinator-directory-scraper` | ~$5/1k all-in | ✓ verified + risky | ✓ | 71% | **Selected** |

**Why fatihtahta won:** It's the only actor under $10/1k that gives verified founder emails AND job descriptions. The 71% success rate is mitigated by our 3-attempt retry loop.

### Key insight: No LLM extraction step needed
The original plan included an LLM extractor to pull `description`, `usp`, `sector` from website text. **Dropped entirely** — fatihtahta already returns `one_liner`, `long_description`, `industry`, `stage`, `team_size`, `tags` in structured JSON from Algolia. Using an LLM to re-extract information Apify gives for free was wasteful.

---

## Fallbacks & Error Handling Decisions

### Scraper (apify_scraper.py)
| Scenario | Handling |
|---|---|
| Apify actor call fails | 3-attempt retry with 5s sleep between attempts |
| All 3 attempts fail | Log + return early, don't crash the server |
| Company has no website | Fall back to YC profile URL (`item.get("url")`) |
| Company has no name | Skip record entirely (can't identify without name) |
| `team_size` is null | `str(team_size or "")` prevents saving literal `"None"` string |

### Contact Saving (base.py)
| Scenario | Handling |
|---|---|
| Risky email (low confidence) | Saved with `email_verified=False`, not discarded — more data > less data |
| Verified email | Saved with `email_verified=True` |
| No email at all | Contact not saved (email is the whole point) |
| Duplicate email | Deduplicate on email only (not name+email) to catch same person across companies |
| Empty email string `""` | Guard: skip dedup query entirely, let it proceed |

### Enrichment Pipeline (pipeline.py)
| Scenario | Handling |
|---|---|
| Website returns 403 | `except Exception` catches it, prints "Could not scrape", continues to next company |
| Company already embedded | Check `Embedding.company_id` before processing, skip if rows exist |
| Empty text returned | `if website_text:` guard, skips embedding step |

### Groq Rate Limits
- `llama-3.1-8b-instant` free tier: 6,000 tokens/minute
- Each extraction call ≈ 1,000 tokens
- `time.sleep(2)` between companies in pipeline keeps us under the limit

---

## Actual vs Planned Data Flow

### Original Plan
```
Scrapers (multiple sources) → Company DB
→ contact_finder (WHOIS/GitHub/Dorks/Mailto) → Contact DB
→ company_summary (LLM extraction) → Company fields
→ news_hook → press hit
→ relevance_scorer → score
→ embeddings (blog/JD) → pgvector
→ LLM email generation
→ Dashboard → Send
```

### Actual Implementation (current state)
```
Apify fatihtahta scraper
    → Company DB (name, website, description, usp, sector, tags, headcount, stage, status)
    → Contact DB (founder name, email, email_verified, linkedin_url, title)
    [One Apify call replaces: scrapers + contact_finder + company_summary]

Enrichment pipeline (pipeline.py)
    → enricher.py: scrapes company homepage with requests + BeautifulSoup
    → embedder.py: chunks text (500 char chunks) → encodes with all-MiniLM-L6-v2 → saves to Embedding table
    [Replaces: rag/ingest.py from original plan]

[NOT BUILT YET] RAG retriever
    → query pgvector for top-k chunks matching email intent
    → return context for prompt

[NOT BUILT YET] LLM email generation
    → Groq: company card + RAG context + your profile → subject + body
    → save EmailDraft

[NOT BUILT YET] Dashboard (Next.js)
[NOT BUILT YET] Email send (Gmail SMTP)
```

---

## Actual File Structure (what exists now)

```
jobangel/
├── backend/
│   ├── app/
│   │   ├── main.py                    ✅ FastAPI app, CORS, router mount
│   │   ├── config.py                  ✅ pydantic-settings (.env loader)
│   │   │
│   │   ├── models/
│   │   │   ├── company.py             ✅ Company ORM model
│   │   │   ├── contact.py             ✅ Contact model (+ email_verified field added)
│   │   │   ├── email_draft.py         ✅ EmailDraft model
│   │   │   ├── outreach.py            ✅ OutreachLog model
│   │   │   └── embedding.py           ✅ Embedding (pgvector Vector(384))
│   │   │
│   │   ├── routers/
│   │   │   └── scrape.py              ✅ POST /scrape/run + POST /scrape/enrich
│   │   │   [companies, emails, outbox, settings routers NOT YET BUILT]
│   │   │
│   │   ├── scrapers/
│   │   │   ├── base.py                ✅ BaseScraper (normalize_domain, save_company, save_contact)
│   │   │   ├── apify_scraper.py       ✅ fatihtahta actor, retry logic, field mapping
│   │   │   ├── enricher.py            ✅ scrape_website_text() via requests + BS4
│   │   │   ├── embedder.py            ✅ chunk_text() + process_and_save_embeddings()
│   │   │   └── pipeline.py            ✅ run_pipeline() — orchestrates enricher + embedder
│   │   │
│   │   ├── llm/
│   │   │   └── extractor.py           ❌ DROPPED — Apify gives structured data directly
│   │   │   [email_generator.py, prompt_builder.py NOT YET BUILT]
│   │   │
│   │   └── db/
│   │       └── session.py             ✅ SQLAlchemy engine, SessionLocal, get_db
│   │
│   ├── migrations/
│   │   └── versions/
│   │       └── 52aa0072bf38_init.py   ✅ Initial schema with pgvector
│   │
│   └── requirements.txt               ✅
│
├── .env                               ✅
└── README.md                          ✅
```

---

## Database Schema (Current Actual)

```
Company
  id, name, website, normalized_domain,
  domain_tags, sector, usp, description,
  funding_amount, funding_round, funding_date,
  headcount_estimate,
  relevance_score, status (new/hiring/emailed/skipped),
  created_at
  UNIQUE(normalized_domain)

Contact
  id, company_id (FK), name, title,
  email, email_verified (bool),       ← added during implementation
  linkedin_url,
  confidence (high/medium/low),
  source (apify_yc / hunter / pattern / manual)

EmailDraft
  id, company_id (FK), contact_id (FK),
  subject, body, status (draft/approved/sent),
  generated_at, edited_at, sent_at

OutreachLog
  id, email_draft_id (FK), sent_at,
  reply_received (bool), reply_at, notes

Embedding
  id, company_id (FK), chunk_text,
  source_type (website / jd / about),
  embedding (Vector(384))
```

---

## RAG — What Gets Embedded

### Original Plan
Blog posts, JD text, about pages, press coverage — all scraped from live websites.

### Revised Plan
**Job descriptions from Apify** are the primary embed source (they contain skills, tech stack, responsibilities — perfect for email personalization). Homepage text from `enricher.py` is a secondary fallback.

Future improvement: embed job description text directly from the Apify JSON instead of / in addition to scraping the homepage.

---

## What's Left to Build (In Order)

1. **RAG Retriever** (`backend/app/rag/retriever.py`)
   - Query pgvector: `SELECT ... ORDER BY embedding <=> $query_vector LIMIT 5`
   - Return top-k chunks for a given company

2. **LLM Email Generator** (`backend/app/llm/email_generator.py`)
   - Groq call with: your profile + company card + RAG chunks + founder bio
   - Returns `subject` + `body` (max ~120 words)
   - `time.sleep(2)` between calls for rate limiting

3. **Email Router** (`backend/app/routers/emails.py`)
   - `POST /emails/generate/{company_id}` — triggers generation, saves EmailDraft
   - `PATCH /emails/{id}` — edit draft
   - `POST /emails/{id}/approve` — marks approved

4. **Gmail SMTP Sender** (`backend/app/email/sender.py`)
   - `smtplib` + port 587 + STARTTLS
   - `POST /outbox/send/{draft_id}`

5. **Frontend** (Next.js 14 — not started)
   - Dashboard: company list with relevance scores, hiring status, email status
   - Company detail: enrichment card + email editor
   - Outbox: approved emails ready to send
   - Settings: profile, Gmail config, Groq key

6. **Additional Scrapers** (after YC pipeline is stable)
   - Indian startup sources: Inc42, YourStory via Apify or custom scraper
   - LinkedIn/Naukri job listings for ML-focused roles
   - Each plugs into the existing `BaseScraper` pipeline

7. **Deploy**
   - Frontend → Vercel (connect GitHub repo, auto-deploy)
   - Backend → Railway or Render (free tier)
   - Supabase stays as-is

---

## Cost Breakdown (Revised)

| Service | Cost |
|---|---|
| Supabase (Postgres + pgvector) | Free (500MB) |
| Groq (LLM) | Free |
| Gmail SMTP | Free (~500 emails/day) |
| sentence-transformers (embedding) | Free (runs locally) |
| Apify fatihtahta (100 companies with emails) | ~$0.70/run, covered by $5/month free credit (~7 runs/month free) |
| **Total** | **$0** |

---

## Environment Variables (Current `.env`)

```
# LLM
GROQ_API_KEY=

# Apify
APIFY_API_TOKEN=

# HuggingFace (optional — suppresses rate limit warning)
HF_TOKEN=

# Email (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password

# Supabase
DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
```
