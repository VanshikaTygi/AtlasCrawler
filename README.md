# AtlasCrawler

An automated data pipeline that scrapes AI startups, products, research papers, news, and jobs, structures the raw data using LLMs, and resolves duplicate entity names — built as a working prototype of a real-time AI industry intelligence system.

## What this project does

AtlasCrawler collects information about what's happening in the AI industry right now — new research papers, startup/product launches, breaking news, and job postings — from live public sources. It then uses a fallback chain of LLMs to turn messy scraped text into clean structured data, and uses fuzzy matching to make sure the same company isn't counted twice under different spellings (e.g., "OpenAI" vs "Open AI"). The final output is pushed into a Google Sheet, ready to be queried or reviewed.

## Architecture overview

```
Scrapers (async) → Raw JSON → LLM Extraction (fallback chain) → Entity Resolution → Google Sheets
```

- **Scrapers** (`scrapers/`): concurrent, async data collection from each source
- **LLM Extraction** (`extractors/`): turns unstructured scraped text into structured JSON, with automatic fallback across three providers
- **Entity Resolution** (`resolution/`): fuzzy-matches raw entity names against a known seed list to produce canonical names
- **Sheets Integration** (`sheets/`): pushes all processed data into a shared Google Sheet across 6 tabs

See `architecture.md` for the full design rationale, including scale strategy and known limitations.

## Data sources

| Category | Source | Method |
|---|---|---|
| Research Papers | Arxiv API | Async REST API pagination |
| Startups / Products | Hacker News (Show HN) via Algolia | Async REST API pagination |
| News | Hacker News via Algolia (date-filtered) | Async REST API, 24h freshness filter |
| Jobs | RemoteOK API | Async REST API, User-Agent spoofing, 24h freshness filter |
| Companies | Y Combinator directory | Playwright (headless browser), JS-rendered content |

## Setup

1. Clone this repository
2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Create a `.env` file with:
   ```
   GEMINI_API_KEY=your_key
   GROQ_API_KEY=your_key
   MISTRAL_API_KEY=your_key
   GOOGLE_SHEET_ID=your_sheet_id
   ```
4. Add your Google service account credentials as `service_account.json` in the project root, and share your target Google Sheet with the service account's email as Editor.

## Running the pipeline

```
python scrapers/arxiv_scraper.py
python scrapers/startup_scraper.py
python scrapers/news_scraper.py
python scrapers/jobs_scraper.py
python scrapers/yc_scraper.py
python extractors/process_yc_data.py
python resolution/apply_resolution.py
python resolution/generate_mapping_log.py
python sheets/push_to_sheets.py
```

## Known limitations

See `architecture.md` for a full, honest account of scope decisions made under the trial's time constraints (e.g., single source per news/jobs category rather than five, no GitHub star tracking for papers, simplified output schema).