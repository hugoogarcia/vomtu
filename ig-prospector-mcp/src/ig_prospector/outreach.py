"""DM generator using Claude API in the prospect's language."""
from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic

MODEL = "claude-opus-4-7"

SYSTEM = """You write short, human-sounding cold DMs for Instagram outreach.
Vomtu is a small content studio that makes short-form product videos for clothing brands.
Rules:
- Write in the language indicated.
- Max 380 characters.
- No emojis unless culturally natural.
- Reference one specific, concrete detail about the brand (product type, vibe, language, platform).
- One soft CTA: ask if they'd be open to seeing 2-3 video ideas.
- Never use "Hope this finds you well" or other AI tells.
- Sound like a real person, not a template.
Return JSON: {"dm": "...", "video_angles": ["...", "...", "..."]}
"""


def _client() -> Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key or key.startswith("REPLACE_"):
        raise RuntimeError("ANTHROPIC_API_KEY missing in .env")
    return Anthropic(api_key=key)


def generate_outreach(profile: dict[str, Any], store: dict[str, Any]) -> dict[str, Any]:
    """Generate a personalized DM + 3 video angle ideas."""
    lang_name = store.get("language_name") or "English"
    user_msg = f"""Brand handle: @{profile.get('username')}
Brand name: {profile.get('fullName') or profile.get('username')}
Bio: {profile.get('biography') or '(empty)'}
Followers: {profile.get('followersCount')}
Store URL: {store.get('url')}
Store platform: {store.get('platform') or 'unknown'}
Store title: {store.get('title')}
Store description: {store.get('description')}
Store content snippet:
{(store.get('content_snippet') or '')[:1200]}

Write the DM in: {lang_name}.
Return ONLY the JSON object, no prose."""

    resp = _client().messages.create(
        model=MODEL,
        max_tokens=600,
        system=SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = resp.content[0].text.strip()
    # strip code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    import json
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"dm": text, "video_angles": []}
