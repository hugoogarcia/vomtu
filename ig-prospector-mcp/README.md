# ig-prospector-mcp

MCP server for discovering Instagram clothing-store prospects in Europe and generating personalized cold DMs in the store's language. Built for Claude Code.

## What it does

1. **Discovers** clothing brands on Instagram via Apify hashtag scraping (configurable seed list).
2. **Filters** by follower range (default 500–50k), recent activity (posted in last 30 days), and presence of a bio link.
3. **Analyzes** each prospect's store via Firecrawl: detects platform (Shopify, WooCommerce, Tiendanube, Wix, …), language, and store signals.
4. **Scores** prospects 0–100 with explainable reasons.
5. **Generates** a personalized DM in the prospect's language + 3 tailored video angles using Claude.
6. **Saves** everything to `data/prospects.csv` (deduped by handle).

## Setup

```bash
cd ig-prospector-mcp
uv venv
source .venv/bin/activate
uv pip install -e .
```

Edit `.env` with your real keys:

```
APIFY_TOKEN=apify_api_...
FIRECRAWL_API_KEY=fc-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Wire into Claude Code

Add to your project `.claude/settings.json` or user `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "ig-prospector": {
      "command": "/Users/hugogarcia/Desktop/Vomtu/ig-prospector-mcp/.venv/bin/python",
      "args": ["-m", "ig_prospector.server"],
      "cwd": "/Users/hugogarcia/Desktop/Vomtu/ig-prospector-mcp"
    }
  }
}
```

Restart Claude Code, then in any session:

> Run the full prospecting pipeline with default hashtags, 30 posts per tag, min score 65, max 15 prospects.

## Tools

| Tool | What it does |
|---|---|
| `discover_prospects` | Apify hashtag scrape → enriched profiles, filtered |
| `analyze_store` | Firecrawl scrape of a single URL → platform + language + signals |
| `score_prospect` | Profile + store → score 0–100 + reasons |
| `generate_outreach` | Claude → DM in store's language + 3 video angles |
| `save_prospect` | Append a single processed prospect to CSV |
| `run_full_pipeline` | One-shot: discover → analyze → score → generate → save |

## Cost expectations (rough)

- Apify hashtag scraper: ~$0.40 per 1000 posts
- Apify profile scraper: ~$2 per 1000 profiles
- Firecrawl: free tier covers 500 scrapes/month
- Anthropic (Opus): ~$0.02 per generated DM

A full pipeline run with 10 hashtags × 30 posts and 15 prospects ≈ $0.80.

## Important

- **Send DMs manually.** This tool prepares the list and the message — IG bans automated DMing. Cap yourself at 20–30 manual DMs/day from a warmed account.
- Respect ToS: the tool only reads public IG data via Apify and public web pages via Firecrawl.
