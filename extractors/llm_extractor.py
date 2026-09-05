import aiohttp
import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")

EXTRACTION_PROMPT = """Extract the following fields from this text as strict JSON only, no explanation, no markdown:
{{
  "entity_name": "",
  "category": "startup/product/paper/news/job",
  "summary": "one sentence summary",
  "date": ""
}}

Text: {text}
"""

async def call_gemini(session, text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": EXTRACTION_PROMPT.format(text=text)}]}]}
    async with session.post(url, json=payload) as resp:
        if resp.status != 200:
            raise Exception(f"Gemini failed: {resp.status}")
        data = await resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

async def call_groq(session, text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": EXTRACTION_PROMPT.format(text=text)}]
    }
    async with session.post(url, json=payload, headers=headers) as resp:
        if resp.status != 200:
            raise Exception(f"Groq failed: {resp.status}")
        data = await resp.json()
        return data["choices"][0]["message"]["content"]

async def call_mistral(session, text):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_KEY}"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": EXTRACTION_PROMPT.format(text=text)}]
    }
    async with session.post(url, json=payload, headers=headers) as resp:
        if resp.status != 200:
            raise Exception(f"Mistral failed: {resp.status}")
        data = await resp.json()
        return data["choices"][0]["message"]["content"]

async def extract_structured_data(session, text):
    for provider_func, name in [(call_gemini, "Gemini"), (call_groq, "Groq"), (call_mistral, "Mistral")]:
        try:
            result = await provider_func(session, text)
            print(f"Succeeded with {name}")
            cleaned = result.strip().strip("```json").strip("```")
            return json.loads(cleaned)
        except Exception as e:
            print(f"{name} failed, trying next: {e}")
    raise Exception("All LLM providers failed")

async def main():
    sample_text = "Acme AI just raised $5M to build autonomous coding agents for enterprise teams, announced September 2026."
    async with aiohttp.ClientSession() as session:
        result = await extract_structured_data(session, sample_text)
        print(result)

if __name__ == "__main__":
    asyncio.run(main())