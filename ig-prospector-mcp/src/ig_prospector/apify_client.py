"""Apify wrapper for Instagram hashtag/profile scraping."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from apify_client import ApifyClient

HASHTAG_ACTOR = "apify/instagram-hashtag-scraper"
PROFILE_ACTOR = "apify/instagram-profile-scraper"


def _client() -> ApifyClient:
    token = os.environ.get("APIFY_TOKEN")
    if not token or token.startswith("REPLACE_"):
        raise RuntimeError("APIFY_TOKEN missing in .env")
    return ApifyClient(token)


def scrape_hashtag_posts(hashtags: list[str], results_per_tag: int = 50) -> list[dict[str, Any]]:
    """Scrape recent posts for hashtags. Returns post items with ownerUsername etc."""
    run_input = {
        "hashtags": hashtags,
        "resultsType": "posts",
        "resultsLimit": results_per_tag,
    }
    run = _client().actor(HASHTAG_ACTOR).call(run_input=run_input)
    return list(_client().dataset(run["defaultDatasetId"]).iterate_items())


def scrape_profiles(usernames: list[str]) -> list[dict[str, Any]]:
    """Enrich a list of usernames with full profile data (followers, bio, link, last post)."""
    if not usernames:
        return []
    run_input = {
        "usernames": usernames,
        "resultsLimit": 1,
    }
    run = _client().actor(PROFILE_ACTOR).call(run_input=run_input)
    return list(_client().dataset(run["defaultDatasetId"]).iterate_items())


def filter_active_recent(
    profiles: list[dict[str, Any]],
    min_followers: int,
    max_followers: int,
    posted_within_days: int,
) -> list[dict[str, Any]]:
    """Apply follower range + recent activity filters."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=posted_within_days)
    out: list[dict[str, Any]] = []
    for p in profiles:
        followers = p.get("followersCount") or 0
        if not (min_followers <= followers <= max_followers):
            continue
        # latestPosts is sorted desc by timestamp on apify profile actor
        latest = (p.get("latestPosts") or [])
        if not latest:
            continue
        ts_str = latest[0].get("timestamp")
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except ValueError:
            continue
        if ts < cutoff:
            continue
        if not p.get("externalUrl") and not p.get("externalUrls"):
            # no link in bio = probably no online store
            continue
        out.append(p)
    return out


def extract_bio_link(profile: dict[str, Any]) -> str | None:
    """Get the primary external URL from a profile."""
    if profile.get("externalUrl"):
        return profile["externalUrl"]
    urls = profile.get("externalUrls") or []
    if urls and isinstance(urls, list):
        first = urls[0]
        if isinstance(first, dict):
            return first.get("url")
        if isinstance(first, str):
            return first
    return None
