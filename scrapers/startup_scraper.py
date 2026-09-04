import aiohttp
import asyncio
import ssl
import certifi
import json

HN_API_URL = "https://hn.algolia.com/api/v1/search"

async def fetch_show_hn_posts(session, total_needed=1200, per_page=100):
    all_posts = []
    for page in range(0, total_needed // per_page):
        params = {
            "tags": "show_hn",
            "hitsPerPage": per_page,
            "page": page
        }
        async with session.get(HN_API_URL, params=params) as response:
            data = await response.json()
            hits = data.get("hits", [])
            if not hits:
                break
            for hit in hits:
                all_posts.append({
                    "title": hit.get("title"),
                    "url": hit.get("url"),
                    "author": hit.get("author"),
                    "points": hit.get("points"),
                    "created_at": hit.get("created_at"),
                    "num_comments": hit.get("num_comments")
                })
            print(f"Fetched page {page}, total so far: {len(all_posts)}")
        await asyncio.sleep(1)
    return all_posts

def save_to_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def main():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        posts = await fetch_show_hn_posts(session)
        print(f"Total fetched: {len(posts)} posts")
        save_to_json(posts, "data/startups.json")
        print("Saved to data/startups.json")

if __name__ == "__main__":
    asyncio.run(main())