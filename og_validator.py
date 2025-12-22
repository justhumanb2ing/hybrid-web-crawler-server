from typing import Dict, Optional
from urllib.parse import urlparse

GENERIC_TITLES = {
    "threads",
    "instagram",
    "facebook",
    "x",
    "log in",
    "sign in",
}

SNS_DOMAINS = {
    "threads.com",
    "www.threads.com",
    "instagram.com",
    "www.instagram.com",
    "x.com",
    "www.x.com",
    "twitter.com",
    "www.twitter.com",
    "facebook.com",
    "www.facebook.com",
}


def is_static_og_valid(
    og: Dict[str, Optional[str]],
    request_url: str,
) -> bool:
    """
    정적 크롤링 결과가 '의미 있는 OG'인지 판단
    """

    title = og.get("title")
    image = og.get("image")

    # 1. 핵심 필드 없음
    if not title or not image:
        return False

    # 2. generic title
    normalized = title.strip().lower()
    if normalized in GENERIC_TITLES:
        return False

    # 3. SNS 도메인 (정적 크롤링 부적합)
    hostname = urlparse(request_url).hostname
    if hostname in SNS_DOMAINS:
        return False

    return True