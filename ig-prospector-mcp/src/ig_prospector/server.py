"""FastMCP server exposing prospecting tools."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)

from . import apify_client, firecrawl_client, outreach, scoring, storage

mcp = FastMCP("ig-prospector")

DEFAULT_HASHTAGS = [
    "smallbusinessuk", "modaespañola", "madeinitaly", "frenchfashion",
    "streetwearberlin", "sustainablefashion", "independentbrand",
    "emergingdesigner", "slowfashion", "handmadeclothing",
]


@mcp.tool()
def discover_prospects(
    hashtags: list[str] | None = None,
    posts_per_hashtag: int = 40,
    min_followers: int = 500,
    max_followers: int = 50000,
    posted_within_days: int = 30,
) -> dict[str, Any]:
    """Discover Instagram clothing-store candidates.

    Pulls recent posts from each hashtag, dedupes the post owners, enriches them
    via the Apify profile scraper, then filters by follower range, recent activity,
    and presence of a bio link. Returns the candidate profiles for downstream
    analysis with `analyze_and_score`. Does NOT consume Firecrawl credits.

    Args:
        hashtags: List of hashtags WITHOUT the # symbol. Defaults to a curated EU
            clothing seed list.
        posts_per_hashtag: How many recent posts to pull per hashtag (cost driver).
        min_followers: Lower bound (inclusive).
        max_followers: Upper bound (inclusive).
        posted_within_days: Profile must have posted in the last N days.

    Returns:
        {"candidates": [profile_dict, ...], "count": int, "sampled_handles": [...]}
    """
    tags = hashtags or DEFAULT_HASHTAGS
    posts = apify_client.scrape_hashtag_posts(tags, results_per_tag=posts_per_hashtag)
    handles = sorted({p["ownerUsername"] for p in posts if p.get("ownerUsername")})
    profiles = apify_client.scrape_profiles(handles)
    filtered = apify_client.filter_active_recent(
        profiles, min_followers, max_followers, posted_within_days
    )
    return {
        "count": len(filtered),
        "sampled_handles": [p.get("username") for p in filtered],
        "candidates": filtered,
    }


@mcp.tool()
def analyze_store(url: str) -> dict[str, Any]:
    """Scrape a storefront URL via Firecrawl and detect platform, language, and store signals.

    Use this to verify a candidate actually runs an online store and to read the
    site's content/language before generating outreach.

    Args:
        url: Full URL of the prospect's store / link-in-bio destination.

    Returns:
        {"ok": bool, "is_store": bool, "platform": str|None, "language": str|None,
         "language_name": str, "title": str, "description": str, "content_snippet": str}
    """
    return firecrawl_client.analyze_store(url)


@mcp.tool()
def score_prospect(profile: dict[str, Any], store: dict[str, Any]) -> dict[str, Any]:
    """Combine a profile dict (from discover_prospects) with a store dict
    (from analyze_store) and return a 0-100 score plus reasoning."""
    score, reasons = scoring.score_prospect(profile, store)
    return {"score": score, "reasons": reasons}


@mcp.tool()
def generate_outreach(profile: dict[str, Any], store: dict[str, Any]) -> dict[str, Any]:
    """Generate a personalized DM (in the store's language) plus 3 video angle ideas
    tailored to the brand. Costs Anthropic API tokens."""
    return outreach.generate_outreach(profile, store)


@mcp.tool()
def save_prospect(
    profile: dict[str, Any],
    store: dict[str, Any],
    score: int,
    score_reasons: list[str],
    outreach_payload: dict[str, Any],
) -> dict[str, Any]:
    """Append a fully-processed prospect to data/prospects.csv (deduped by handle)."""
    row = {
        "handle": profile.get("username"),
        "full_name": profile.get("fullName"),
        "followers": profile.get("followersCount"),
        "bio": (profile.get("biography") or "").replace("\n", " "),
        "store_url": store.get("url"),
        "platform": store.get("platform"),
        "language": store.get("language"),
        "score": score,
        "score_reasons": " | ".join(score_reasons),
        "dm": outreach_payload.get("dm", ""),
        "video_angles": " | ".join(outreach_payload.get("video_angles", [])),
        "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    written = storage.append_prospects([row])
    return {"written": written, "csv_path": storage.csv_path_str(), "handle": row["handle"]}


@mcp.tool()
def run_full_pipeline(
    hashtags: list[str] | None = None,
    posts_per_hashtag: int = 30,
    min_followers: int = 500,
    max_followers: int = 50000,
    posted_within_days: int = 30,
    min_score: int = 60,
    max_to_process: int = 20,
) -> dict[str, Any]:
    """End-to-end: discover → analyze → score → generate DM → save to CSV.

    This is the one-shot tool. It walks every step and writes qualifying prospects
    (score >= min_score) to data/prospects.csv. Hard cap via max_to_process to
    keep API costs bounded per run.

    Returns a summary with counts and the CSV path.
    """
    candidates = discover_prospects(
        hashtags=hashtags,
        posts_per_hashtag=posts_per_hashtag,
        min_followers=min_followers,
        max_followers=max_followers,
        posted_within_days=posted_within_days,
    )["candidates"]

    saved = 0
    skipped_no_link = 0
    skipped_low_score = 0
    errors: list[str] = []

    for profile in candidates[:max_to_process]:
        link = apify_client.extract_bio_link(profile)
        if not link:
            skipped_no_link += 1
            continue
        try:
            store = firecrawl_client.analyze_store(link)
            score, reasons = scoring.score_prospect(profile, store)
            if score < min_score:
                skipped_low_score += 1
                continue
            dm_payload = outreach.generate_outreach(profile, store)
            row = {
                "handle": profile.get("username"),
                "full_name": profile.get("fullName"),
                "followers": profile.get("followersCount"),
                "bio": (profile.get("biography") or "").replace("\n", " "),
                "store_url": store.get("url"),
                "platform": store.get("platform"),
                "language": store.get("language"),
                "score": score,
                "score_reasons": " | ".join(reasons),
                "dm": dm_payload.get("dm", ""),
                "video_angles": " | ".join(dm_payload.get("video_angles", [])),
                "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            saved += storage.append_prospects([row])
        except Exception as e:
            errors.append(f"{profile.get('username')}: {e}")

    return {
        "total_candidates": len(candidates),
        "processed": min(len(candidates), max_to_process),
        "saved": saved,
        "skipped_no_link": skipped_no_link,
        "skipped_low_score": skipped_low_score,
        "errors": errors,
        "csv_path": storage.csv_path_str(),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
