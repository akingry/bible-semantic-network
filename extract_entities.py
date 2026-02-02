"""
Extract People and Places from Bible using spaCy NER
Runs locally - no API tokens needed.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

print("Loading spaCy with NER...")
import spacy
nlp = spacy.load("en_core_web_sm")  # Has NER built in
print("spaCy loaded")


def parse_bible(filepath):
    """Parse NASB Bible into chapters."""
    print(f"Reading {filepath}...")
    content = Path(filepath).read_text(encoding='utf-8')
    
    pattern = re.compile(
        r'^(.+?)\s+--\s+(\d?\s?[a-zA-Z]+(?:\s+of\s+[a-zA-Z]+|\s+[a-zA-Z]+)?)\s+(\d+):(\d+)\s*$',
        re.IGNORECASE
    )
    
    chapters = defaultdict(list)
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line == '.':
            continue
        
        match = pattern.match(line)
        if match:
            text, book, chapter, verse = match.groups()
            book = book.strip().title()
            chapter_key = f"{book} {chapter}"
            chapters[chapter_key].append(text)
    
    return {k: " ".join(v) for k, v in chapters.items()}


def extract_entities(bible_filepath, concordance_filepath, output_filepath="entities.json"):
    """Extract people and places using spaCy NER."""
    
    chapters = parse_bible(bible_filepath)
    print(f"Loaded {len(chapters)} chapters")
    
    # Load concordance to check which words are actually indexed
    print("Loading concordance...")
    with open(concordance_filepath, 'r', encoding='utf-8') as f:
        concordance = json.load(f)
    indexed_words = set(concordance['concordance'].keys())
    print(f"  {len(indexed_words)} indexed words")
    
    # Entity containers
    people = defaultdict(int)   # entity -> count of chapters
    places = defaultdict(int)
    
    # Process each chapter
    print("Extracting entities...")
    for idx, (chapter_key, text) in enumerate(chapters.items()):
        if idx % 100 == 0:
            print(f"  Processing chapter {idx + 1}/{len(chapters)}...")
        
        doc = nlp(text)
        
        chapter_people = set()
        chapter_places = set()
        
        for ent in doc.ents:
            # Normalize: lowercase, strip
            name = ent.text.lower().strip()
            
            # Skip very short or multi-word for now
            if len(name) < 3 or ' ' in name:
                continue
            
            # Skip if not in concordance (won't be searchable anyway)
            if name not in indexed_words:
                continue
            
            if ent.label_ == 'PERSON':
                chapter_people.add(name)
            elif ent.label_ in ('GPE', 'LOC', 'FAC'):
                # GPE = countries/cities, LOC = mountains/rivers, FAC = buildings
                chapter_places.add(name)
        
        # Count chapters (not total occurrences)
        for p in chapter_people:
            people[p] += 1
        for p in chapter_places:
            places[p] += 1
    
    # Filter: require at least 2 chapter appearances to reduce noise
    people = {k: v for k, v in people.items() if v >= 2}
    places = {k: v for k, v in places.items() if v >= 2}
    
    # Sort by frequency
    people_sorted = sorted(people.keys(), key=lambda x: -people[x])
    places_sorted = sorted(places.keys(), key=lambda x: -places[x])
    
    print(f"\nFound {len(people_sorted)} people, {len(places_sorted)} places")
    
    # Save
    output = {
        "people": people_sorted,
        "places": places_sorted,
        "people_counts": people,
        "places_counts": places
    }
    
    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to {output_filepath}")
    
    # Show top results
    print(f"\nTop 20 People:")
    for p in people_sorted[:20]:
        print(f"  {p}: {people[p]} chapters")
    
    print(f"\nTop 20 Places:")
    for p in places_sorted[:20]:
        print(f"  {p}: {places[p]} chapters")
    
    return people_sorted, places_sorted


if __name__ == "__main__":
    extract_entities("nasb.txt", "concordance.json", "entities.json")
