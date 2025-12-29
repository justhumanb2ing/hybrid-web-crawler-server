from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import os
from dotenv import load_dotenv

from app.dependencies import require_signed_in_user
from app.services.crawler_service import crawl_with_fallback

load_dotenv()

app = FastAPI(title="Hybrid Crawler")

# ✅ 허용할 프론트엔드 도메인들
origins = os.getenv("CORS_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    url: HttpUrl

@app.post("/crawl")
def crawl(req: CrawlRequest, _: None = Depends(require_signed_in_user)):
    try:
        data = crawl_with_fallback(str(req.url))
        return {
            "success": True,
            "data": data,
        }

    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    
@app.get("/health")
def health():
    return {"status": "ok"}
