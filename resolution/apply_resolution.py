import json
import os
from entity_resolver import resolve_entity_name

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_PATH = os.path.join(SCRIPT_DIR, "..", "data", "jobs.json")

def resolve_jobs_companies(filepath=JOBS_PATH):
    jobs = load_json(filepath)
    for job in jobs:
        raw_company = job.get("company")
        job["resolved_company"] = resolve_entity_name(raw_company)
    save_json(jobs, filepath)
    print(f"Resolved company names for {len(jobs)} jobs")

if __name__ == "__main__":
    resolve_jobs_companies()