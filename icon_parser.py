from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional, Tuple


ICON_RELS = {
    "icon",
    "shortcut icon",
    "apple-touch-icon",
    "apple-touch-icon-precomposed",
}


def _parse_size(size_str: str) -> int:
    """
    sizes="32x32" -> 32
    sizes="180x180" -> 180
    sizes="any" -> 큰 값 (보통 SVG)
    """
    if not size_str:
        return 0

    s = size_str.lower().strip()
    if s == "any":
        return 10_000

    if "x" in s:
        try:
            return int(s.split("x")[0])
        except ValueError:
            return 0

    return 0


def _is_svg(href: str) -> bool:
    # querystring 포함 케이스도 처리: icon.svg?v=1
    return href.lower().split("?", 1)[0].endswith(".svg")


def parse_icon(html: str, request_url: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")

    # candidates: (svg_priority, size_score, url)
    # svg_priority: 1이면 SVG, 0이면 비-SVG
    candidates: list[Tuple[int, int, str]] = []

    for link in soup.find_all("link"):
        rel = link.get("rel")
        href = link.get("href")
        if not rel or not href:
            continue

        rel_joined = " ".join(rel).lower()
        if not any(r in rel_joined for r in ICON_RELS):
            continue

        size_score = _parse_size(link.get("sizes", ""))
        svg_priority = 1 if (_is_svg(href) or (link.get("sizes", "").strip().lower() == "any")) else 0
        icon_url = urljoin(request_url, href)

        candidates.append((svg_priority, size_score, icon_url))

    if candidates:
        # 1) SVG 우선, 2) sizes 큰 것 우선
        candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return candidates[0][2]

    # fallback: /favicon.ico
    parsed = urlparse(request_url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"

    return None