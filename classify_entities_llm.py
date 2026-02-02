"""
Classify People and Places using Local LLM (LM Studio)
More accurate than spaCy NER for Biblical text.
Processes in batches to minimize LLM calls.
"""

import json
import requests
from pathlib import Path

LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"

def call_llm(prompt, max_tokens=500):
    """Send prompt to LM Studio."""
    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": "You are a Biblical scholar. Classify words accurately and concisely."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"LLM error: {e}")
        return ""


def classify_batch(words, category):
    """Classify a batch of words as people or places."""
    word_list = ", ".join(words)
    
    if category == "people":
        prompt = f"""From this list of words, identify ONLY the ones that are names of people in the Bible (prophets, kings, apostles, etc).
Return ONLY the names that are actual people, one per line. Skip any common English words.

Words: {word_list}

People (one per line):"""
    else:
        prompt = f"""From this list of words, identify ONLY the ones that are place names in the Bible (cities, regions, rivers, mountains, etc).
Return ONLY the names that are actual places, one per line. Skip any common English words.

Words: {word_list}

Places (one per line):"""
    
    response = call_llm(prompt, max_tokens=len(words) * 15)
    
    # Parse response - extract words that match our input
    valid = set()
    words_lower = {w.lower() for w in words}
    
    for line in response.split('\n'):
        word = line.strip().lower()
        # Remove any numbering or bullets
        word = word.lstrip('0123456789.-) ').strip()
        if word in words_lower:
            valid.add(word)
    
    return valid


def main():
    # Load concordance to get indexed words
    print("Loading concordance...")
    with open("concordance.json", 'r', encoding='utf-8') as f:
        concordance = json.load(f)
    
    indexed_words = list(concordance['concordance'].keys())
    print(f"  {len(indexed_words)} indexed words")
    
    # Filter to likely proper nouns (skip very common words)
    common_words = {
        'the', 'and', 'for', 'with', 'that', 'this', 'from', 'have', 'will',
        'said', 'saying', 'come', 'came', 'went', 'going', 'make', 'made',
        'take', 'took', 'give', 'gave', 'bring', 'brought', 'speak', 'spoke',
        'stand', 'stood', 'evil', 'good', 'great', 'many', 'shall', 'king',
        'lord', 'god', 'son', 'sons', 'man', 'men', 'people', 'word', 'words',
        'day', 'days', 'time', 'year', 'years', 'hand', 'hands', 'face',
        'eye', 'eyes', 'heart', 'house', 'land', 'city', 'place', 'way',
        'thing', 'things', 'life', 'death', 'name', 'seek', 'find', 'found',
        'know', 'knew', 'see', 'saw', 'hear', 'heard', 'tell', 'told',
        'let', 'put', 'set', 'turn', 'call', 'called', 'answer', 'answered',
        'behold', 'therefore', 'thus', 'also', 'even', 'now', 'then', 'yet',
        'because', 'according', 'against', 'before', 'after', 'above', 'below',
        'among', 'between', 'under', 'over', 'through', 'into', 'upon',
        'arise', 'say', 'like', 'just', 'being', 'become', 'becoming'
    }
    
    # Get candidates (exclude very common words and very short words)
    candidates = [w for w in indexed_words 
                  if len(w) >= 4 and w not in common_words]
    
    print(f"  {len(candidates)} candidates to classify")
    
    # Check LM Studio
    try:
        requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
        print("Connected to LM Studio")
    except:
        print("ERROR: LM Studio not running!")
        return
    
    # Classify in batches
    batch_size = 50
    all_people = set()
    all_places = set()
    
    print(f"\nClassifying people ({len(candidates)} candidates)...")
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i + batch_size]
        print(f"  Batch {i//batch_size + 1}/{(len(candidates) + batch_size - 1)//batch_size}...")
        people = classify_batch(batch, "people")
        all_people.update(people)
    
    print(f"\nClassifying places ({len(candidates)} candidates)...")
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i + batch_size]
        print(f"  Batch {i//batch_size + 1}/{(len(candidates) + batch_size - 1)//batch_size}...")
        places = classify_batch(batch, "places")
        all_places.update(places)
    
    # Get chapter counts from concordance
    people_with_counts = {p: len(concordance['concordance'].get(p, [])) 
                         for p in all_people if p in concordance['concordance']}
    places_with_counts = {p: len(concordance['concordance'].get(p, [])) 
                         for p in all_places if p in concordance['concordance']}
    
    # Sort by count
    people_sorted = sorted(people_with_counts.keys(), key=lambda x: -people_with_counts[x])
    places_sorted = sorted(places_with_counts.keys(), key=lambda x: -places_with_counts[x])
    
    print(f"\n{'='*50}")
    print(f"CLASSIFICATION COMPLETE")
    print(f"{'='*50}")
    print(f"  People: {len(people_sorted)}")
    print(f"  Places: {len(places_sorted)}")
    
    # Save
    output = {
        "people": people_sorted,
        "places": places_sorted,
        "people_counts": people_with_counts,
        "places_counts": places_with_counts
    }
    
    with open("entities.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to entities.json")
    
    print(f"\nTop 30 People:")
    for p in people_sorted[:30]:
        print(f"  {p}: {people_with_counts[p]} chapters")
    
    print(f"\nTop 30 Places:")
    for p in places_sorted[:30]:
        print(f"  {p}: {places_with_counts[p]} chapters")


if __name__ == "__main__":
    main()
