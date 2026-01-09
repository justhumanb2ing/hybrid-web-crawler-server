from playwright.sync_api import sync_playwright

from app.parsing.og import parse_og


class DynamicCrawlError(Exception):
    pass


def dynamic_crawl(url: str):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_load_state("networkidle")

            html = page.content()
            browser.close()

            return parse_og(html, url)

    except Exception as e:
        raise DynamicCrawlError(str(e))
