from enum import Enum
from urllib.parse import urlparse


class CrawlStrategy(str, Enum):
    STATIC_ONLY = "static_only"
    DYNAMIC_ONLY = "dynamic_only"
    HYBRID = "hybrid"


# 🔥 도메인별 전략 캐시 (in-memory)
_domain_strategy_cache: dict[str, CrawlStrategy] = {}


def get_domain(url: str) -> str:
    return urlparse(url).hostname or ""


def get_strategy(url: str) -> CrawlStrategy:
    domain = get_domain(url)
    return _domain_strategy_cache.get(domain, CrawlStrategy.HYBRID)


def set_strategy(url: str, strategy: CrawlStrategy):
    domain = get_domain(url)
    _domain_strategy_cache[domain] = strategy