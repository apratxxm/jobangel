# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import scrape

app = FastAPI(title="JobAngel API")

# Allow the Next.js frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "JobAngel backend is running!"}

# attaching the router
app.include_router(scrape.router, prefix="/scrape", tags=["Scraping"])