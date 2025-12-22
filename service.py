from static_crawler import static_crawl, StaticCrawlError
from dynamic_crawler import dynamic_crawl
from og_validator import is_static_og_valid
from strategy_cache import (
    get_strategy,
    set_strategy,
    CrawlStrategy,
)


def crawl_with_fallback(url: str):
    strategy = get_strategy(url)

    # 1️⃣ 정적만 쓰는 도메인
    if strategy == CrawlStrategy.STATIC_ONLY:
        og = static_crawl(url)
        og["crawl_type"] = "static"
        return og

    # 2️⃣ 동적만 쓰는 도메인
    if strategy == CrawlStrategy.DYNAMIC_ONLY:
        og = dynamic_crawl(url)
        og["crawl_type"] = "dynamic"
        return og

    # 3️⃣ HYBRID (기본)
    try:
        og = static_crawl(url)

        if is_static_og_valid(og, url):
            # ✅ 정적 성공 → 캐시 업데이트
            set_strategy(url, CrawlStrategy.STATIC_ONLY)
            og["crawl_type"] = "static"
            return og

        # ❌ 의미 없는 OG
        raise StaticCrawlError("Static OG invalid")

    except StaticCrawlError:
        og = dynamic_crawl(url)

        # 🔥 동적 성공 → 이 도메인은 동적 전용
        set_strategy(url, CrawlStrategy.DYNAMIC_ONLY)

        og["crawl_type"] = "dynamic"
        return og