from bs4 import BeautifulSoup
from typing import Dict, Optional

from app.parsing.icon import parse_icon
from app.storage.r2 import upload_asset_from_url


def parse_og(html: str, request_url: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "html.parser")

    def og(prop: str):
        tag = soup.find("meta", property=prop)
        return tag["content"] if tag and tag.get("content") else None

    image_url = og("og:image")
    icon_url = parse_icon(html, request_url)

    return {
        "title": og("og:title") or (soup.title.string if soup.title else None),
        "description": og("og:description"),
        "image": upload_asset_from_url(image_url, "image"),
        "site_name": og("og:site_name"),
        "url": og("og:url") or request_url,
        "icon": upload_asset_from_url(icon_url, "icon"),
    }
