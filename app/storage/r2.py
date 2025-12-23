import hashlib
import mimetypes
import os
from typing import Optional
from urllib.parse import urlparse

import boto3
from botocore.config import Config
import requests


_R2_ENDPOINT = os.getenv("R2_ENDPOINT")
_R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
_R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
_R2_BUCKET = os.getenv("R2_BUCKET")
_R2_PUBLIC_BASE_URL = os.getenv("R2_PUBLIC_BASE_URL")
_R2_REGION = os.getenv("R2_REGION", "auto")
_R2_PREFIX = os.getenv("R2_PREFIX", "crawl")

_R2_URL_PREFIX = _R2_PUBLIC_BASE_URL.rstrip("/") if _R2_PUBLIC_BASE_URL else None
_R2_CLIENT = None

_DOWNLOAD_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _r2_enabled() -> bool:
    return all(
        [
            _R2_ENDPOINT,
            _R2_ACCESS_KEY_ID,
            _R2_SECRET_ACCESS_KEY,
            _R2_BUCKET,
            _R2_PUBLIC_BASE_URL,
        ]
    )


def _get_r2_client():
    global _R2_CLIENT
    if _R2_CLIENT is None:
        _R2_CLIENT = boto3.client(
            "s3",
            endpoint_url=_R2_ENDPOINT,
            aws_access_key_id=_R2_ACCESS_KEY_ID,
            aws_secret_access_key=_R2_SECRET_ACCESS_KEY,
            region_name=_R2_REGION,
            config=Config(signature_version="s3v4"),
        )
    return _R2_CLIENT


def _extension_for(content_type: str, source_url: str) -> str:
    ext = ""
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";", 1)[0].strip()) or ""
        if ext == ".jpe":
            ext = ".jpg"
    if not ext:
        ext = os.path.splitext(urlparse(source_url).path)[1]
    if ext and not ext.startswith("."):
        ext = f".{ext}"
    return ext or ".bin"


def _is_public_r2_url(url: str) -> bool:
    return bool(_R2_URL_PREFIX) and url.startswith(_R2_URL_PREFIX)


def upload_asset_from_url(source_url: Optional[str], kind: str) -> Optional[str]:
    if not source_url:
        return None
    if not _r2_enabled() or _is_public_r2_url(source_url):
        return source_url

    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"}:
        return source_url

    try:
        response = requests.get(
            source_url,
            headers=_DOWNLOAD_HEADERS,
            timeout=8,
        )
        response.raise_for_status()
    except Exception:
        return source_url

    content = response.content
    if not content:
        return source_url

    content_type = response.headers.get("Content-Type", "")
    extension = _extension_for(content_type, source_url)
    digest = hashlib.sha256(content).hexdigest()
    prefix = digest[:2]
    key = f"{_R2_PREFIX}/{kind}/{prefix}/{digest}{extension}"

    try:
        client = _get_r2_client()
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type.split(";", 1)[0].strip()
        client.put_object(Bucket=_R2_BUCKET, Key=key, Body=content, **extra_args)
    except Exception:
        return source_url

    return f"{_R2_PUBLIC_BASE_URL.rstrip('/')}/{key}"
