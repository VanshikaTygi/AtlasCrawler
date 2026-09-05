import aiohttp
import asyncio
import ssl
import certifi
import json
import time

HN_SEARCH_URL = "http://hn.algolia.com/api/v1/search_by_date"

async def fetch_recent_ai_news(session, hours_back=24, per_page=100, max_pages=10):
    cutoff_timestamp = int(time.time()) - (hours_back * 3600)
    all_articles = []
    for page in range(max_pages):
        params = {
            "query": "AI",
            "tags": "story",
            "numericFilters": f"created_at_i>{cutoff_timestamp}",
            "hitsPerPage": per_page,
            "page": page
        }
        async with session.get(HN_SEARCH_URL, params=params) as response:
            data = await response.json()
            hits = data.get("hits", [])
            if not hits:
                break
            for hit in hits:
                all_articles.append({
                    "title": hit.get("title"),
                    "url": hit.get("url"),
                    "author": hit.get("author"),
                    "points": hit.get("points"),
                    "created_at": hit.get("created_at"),
                    "num_comments": hit.get("num_comments")
                })
            print(f"Fetched page {page}, total so far: {len(all_articles)}")
        await asyncio.sleep(1)
    return all_articles

def save_to_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def main():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        articles = await fetch_recent_ai_news(session)
        print(f"Total fetched: {len(articles)} articles from the last 24 hours")
        save_to_json(articles, "data/news.json")
        print("Saved to data/news.json")

if __name__ == "__main__":
    asyncio.run(main())