import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import save_to_json, create_ssl_connector


ARXIV_API_URL = "http://export.arxiv.org/api/query"


async def fetch_arxiv_papers(session, query="artificial intelligence", total_needed=1200, batch_size=100):
    all_papers = []
    for start in range(0, total_needed, batch_size):
        params = {
            "search_query": f"all:{query}",
            "start": start,
            "max_results": batch_size,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        async with session.get(ARXIV_API_URL, params=params) as response:
            xml_text = await response.text()
            batch = parse_arxiv_response(xml_text)
            all_papers.extend(batch)
            print(f"Fetched batch starting at {start}, total so far: {len(all_papers)}")
        await asyncio.sleep(3)  # be polite to Arxiv's servers
    return all_papers

def parse_arxiv_response(xml_text):
    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    papers = []
    for entry in root.findall("atom:entry", ns):
        papers.append({
            "title": entry.find("atom:title", ns).text.strip(),
            "summary": entry.find("atom:summary", ns).text.strip(),
            "published": entry.find("atom:published", ns).text,
            "link": entry.find("atom:id", ns).text,
            "authors": [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
        })
    return papers

async def main():
    connector = create_ssl_connector()
    async with aiohttp.ClientSession(connector=connector) as session:
        papers = await fetch_arxiv_papers(session)
        print(f"Total fetched: {len(papers)} papers")
        save_to_json(papers, "data/papers.json")
        print("Saved to data/papers.json")


if __name__ == "__main__":
    asyncio.run(main())