"""Scoring logic for prospects."""
from __future__ import annotations

from typing import Any

EU_LANGS = {"es", "en", "fr", "it", "de", "pt", "nl", "ca"}


def score_prospect(profile: dict[str, Any], store: dict[str, Any]) -> tuple[int, list[str]]:
    """Return (score 0-100, reasons list)."""
    score = 0
    reasons: list[str] = []

    if store.get("ok") and store.get("is_store"):
        score += 35
        reasons.append("confirmed online store")
    else:
        reasons.append("store not confirmed — manual check needed")

    if store.get("platform"):
        score += 15
        reasons.append(f"runs on {store['platform']}")

    lang = store.get("language")
    if lang in EU_LANGS:
        score += 10
        reasons.append(f"european language ({lang})")

    followers = profile.get("followersCount") or 0
    if 1000 <= followers <= 25000:
        score += 20
        reasons.append("sweet-spot follower range (1k–25k)")
    elif 500 <= followers < 1000 or 25000 < followers <= 50000:
        score += 12
        reasons.append("acceptable follower range")

    bio = (profile.get("biography") or "").lower()
    fashion_keywords = ["clothing", "ropa", "fashion", "moda", "wear", "apparel",
                        "streetwear", "boutique", "atelier", "kleidung", "abbigliamento",
                        "vêtements", "roupa", "brand", "marca"]
    if any(k in bio for k in fashion_keywords):
        score += 10
        reasons.append("fashion keywords in bio")

    posts = profile.get("postsCount") or 0
    if posts >= 30:
        score += 5
        reasons.append("active history (30+ posts)")

    if profile.get("verified"):
        score += 5
        reasons.append("verified account")

    return min(score, 100), reasons
