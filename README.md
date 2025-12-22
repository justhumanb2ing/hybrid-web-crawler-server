# Hybrid Crawler

Static + Dynamic crawler with automatic fallback.

## Features
- Static crawling (requests + BeautifulSoup)
- Dynamic crawling (Playwright)
- Automatic fallback
- Domain-based crawl strategy caching
- OG metadata extraction

## Run
```bash
pip install -r requirements.txt
playwright install chromium
uvicorn main:app --reload