from rapidfuzz import fuzz, process

KNOWN_ENTITIES = [
    "OpenAI", "Anthropic", "Google DeepMind", "Meta AI", "Mistral AI",
    "Cohere", "Hugging Face", "Stability AI", "xAI", "Perplexity AI",
    "Groq", "Together AI", "Runway", "Midjourney", "Character AI",
    "Inflection AI", "Adept AI", "Scale AI", "Databricks", "NVIDIA"
]

def resolve_entity_name(raw_name, threshold=85):
    if not raw_name:
        return None
    match = process.extractOne(raw_name, KNOWN_ENTITIES, scorer=fuzz.WRatio, processor=lambda x: x.lower())
    if match and match[1] >= threshold:
        return match[0]
    return raw_name

if __name__ == "__main__":
    test_names = ["Open AI", "openai", "Anthropic PBC", "DeepMind", "Some New Startup"]
    for name in test_names:
        print(f"{name} -> {resolve_entity_name(name)}")