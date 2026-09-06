import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def build_mapping_log():
    log = []

    jobs = load_json(os.path.join(DATA_DIR, "jobs.json"))
    for job in jobs:
        raw = job.get("company")
        resolved = job.get("resolved_company")
        if raw:
            log.append({"raw_name": raw, "canonical_name": resolved, "source": "jobs"})

    companies_path = os.path.join(DATA_DIR, "yc_companies_structured.json")
    if os.path.exists(companies_path):
        companies = load_json(companies_path)
        for c in companies:
            raw = c.get("entity_name")
            resolved = c.get("resolved_company")
            if raw:
                log.append({"raw_name": raw, "canonical_name": resolved, "source": "yc_companies"})

    save_json(log, os.path.join(DATA_DIR, "entity_mapping_log.json"))
    print(f"Built entity mapping log with {len(log)} entries")

if __name__ == "__main__":
    build_mapping_log()