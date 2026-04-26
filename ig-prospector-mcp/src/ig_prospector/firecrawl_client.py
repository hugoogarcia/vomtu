"""Firecrawl wrapper to analyze prospect storefronts (firecrawl-py v4 / v2 API)."""
from __future__ import annotations

import os
import re
from typing import Any

from firecrawl import Firecrawl

PLATFORM_SIGNATURES = {
    "shopify": [r"cdn\.shopify\.com", r"Shopify\.theme", r"/cdn/shop/"],
    "woocommerce": [r"wp-content/plugins/woocommerce", r"woocommerce-"],
    "tiendanube": [r"tiendanube", r"mitiendanube"],
    "wix": [r"static\.wixstatic\.com", r"wix\.com"],
    "squarespace": [r"squarespace\.com", r"static1\.squarespace"],
    "prestashop": [r"prestashop"],
    "bigcartel": [r"bigcartel"],
    "etsy": [r"etsy\.com"],
}

LANG_TO_NAME = {
    "es": "Spanish", "en": "English", "fr": "French", "it": "Italian",
    "de": "German", "pt": "Portuguese", "nl": "Dutch", "ca": "Catalan",
}


def _client() -> Firecrawl:
    key = os.environ.get("FIRECRAWL_API_KEY")
    if not key or key.startswith("REPLACE_"):
        raise RuntimeError("FIRECRAWL_API_KEY missing in .env")
    return Firecrawl(api_key=key)


def analyze_store(url: str) -> dict[str, Any]:
    """Scrape a storefront URL and extract platform, language, and a content snippet."""
    try:
        doc = _client().scrape(url, formats=["markdown", "html"], only_main_content=False, timeout=30000)
    except Exception as e:
        return {"url": url, "ok": False, "error": str(e)}

    html = (getattr(doc, "html", None) or "")[:200_000]
    markdown = (getattr(doc, "markdown", None) or "")[:8000]
    md = getattr(doc, "metadata", None)
    metadata: dict[str, Any] = {}
    if md is not None:
        if hasattr(md, "model_dump"):
            metadata = md.model_dump(exclude_none=True)
        elif isinstance(md, dict):
            metadata = md

    platform = _detect_platform(html)
    lang = _detect_language(html, metadata)
    title = metadata.get("title") or ""
    description = metadata.get("description") or ""

    is_store = bool(platform) or _looks_like_store(html, markdown)

    return {
        "url": url,
        "ok": True,
        "is_store": is_store,
        "platform": platform,
        "language": lang,
        "language_name": LANG_TO_NAME.get(lang or "", lang or "Unknown"),
        "title": title,
        "description": description,
        "content_snippet": markdown[:2000],
    }


def _detect_platform(html: str) -> str | None:
    low = html.lower()
    for name, patterns in PLATFORM_SIGNATURES.items():
        for pat in patterns:
            if re.search(pat, low):
                return name
    return None


def _detect_language(html: str, metadata: dict[str, Any]) -> str | None:
    for key in ("language", "lang", "ogLocale"):
        v = metadata.get(key)
        if v:
            return str(v).lower()[:2]
    m = re.search(r'<html[^>]+lang="([a-zA-Z\-]+)"', html)
    if m:
        return m.group(1).lower()[:2]
    return None


def _looks_like_store(html: str, markdown: str) -> bool:
    blob = (html + " " + markdown).lower()
    signals = ["add to cart", "añadir al carrito", "ajouter au panier",
               "carrello", "warenkorb", "comprar", "checkout", "shop now",
               "envío", "shipping", "livraison", "free shipping"]
    return any(s in blob for s in signals)
