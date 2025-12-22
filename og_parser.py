from bs4 import BeautifulSoup
from typing import Dict, Optional


def parse_og(html: str, request_url: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "html.parser")

    def og(prop: str):
        tag = soup.find("meta", property=prop)
        return tag["content"] if tag and tag.get("content") else None

    return {
        "title": og("og:title") or (soup.title.string if soup.title else None),
        "description": og("og:description"),
        "image": og("og:image"),
        "site_name": og("og:site_name"),
        "url": og("og:url") or request_url,
    }