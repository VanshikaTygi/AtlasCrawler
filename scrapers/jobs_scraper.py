import aiohttp
import asyncio
import ssl
import certifi
import json
import time
from datetime import datetime, timezone
import re

REMOTEOK_URL = "https://remoteok.com/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

AI_PATTERNS = [
    r"\bai\b", r"\bml\b", r"\bllm\b", r"\bnlp\b",
    r"machine learning", r"deep learning", r"data scien",
    r"artificial intelligence", r"generative ai", r"large language model"
]

def is_ai_job(job):
    haystack = " ".join([
        job.get("position", "") or "",
        job.get("description", "") or "",
        " ".join(job.get("tags", []) or [])
    ]).lower()
    return any(re.search(pattern, haystack) for pattern in AI_PATTERNS)

async def fetch_ai_jobs(session, hours_back=24):
    async with session.get(REMOTEOK_URL, headers=HEADERS) as response:
        if response.status != 200:
            raise Exception(f"RemoteOK failed: {response.status}")
        all_jobs = await response.json()
        print(f"Total jobs fetched from RemoteOK: {len(all_jobs)}")

    cutoff_timestamp = time.time() - (hours_back * 3600)
    recent_ai_jobs = []

    for job in all_jobs:
        if not isinstance(job, dict) or "date" not in job:
            continue

        if not is_ai_job(job):
            continue

        job_time = datetime.fromisoformat(job["date"].replace("Z", "+00:00"))
        job_timestamp = job_time.timestamp()

        if job_timestamp >= cutoff_timestamp:
            recent_ai_jobs.append({
                "position": job.get("position"),
                "company": job.get("company"),
                "url": job.get("url"),
                "date": job.get("date"),
                # "tags": tags
            })

    return recent_ai_jobs

def save_to_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def main():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        jobs = await fetch_ai_jobs(session)
        print(f"Total fetched: {len(jobs)} AI jobs from the last 24 hours")
        save_to_json(jobs, "data/jobs.json")
        print("Saved to data/jobs.json")

if __name__ == "__main__":
    asyncio.run(main())