"""
Extract ALL proper nouns from Bible text by finding capitalized words.
This catches every name, including obscure genealogical names.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Words that are capitalized but NOT proper nouns
COMMON_WORDS_CAPS = {
    # Start of sentence words, common titles, etc.
    'the', 'a', 'an', 'and', 'or', 'but', 'for', 'so', 'yet', 'in', 'on', 'at',
    'to', 'of', 'by', 'with', 'from', 'as', 'if', 'then', 'when', 'while',
    'after', 'before', 'because', 'though', 'although', 'until', 'unless',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'who', 'what', 'which',
    'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'our', 'their',
    'all', 'every', 'each', 'any', 'some', 'no', 'none', 'many', 'much', 'few',
    'now', 'then', 'here', 'there', 'where', 'how', 'why', 'therefore',
    'behold', 'thus', 'truly', 'verily', 'surely', 'indeed', 'certainly',
    'amen', 'selah', 'hallelujah', 'hosanna', 'alleluia',
    'oh', 'o', 'ah', 'alas', 'woe', 'lo', 'hark',
    'let', 'may', 'shall', 'will', 'would', 'should', 'could', 'can', 'must',
    'do', 'does', 'did', 'have', 'has', 'had', 'be', 'am', 'is', 'are', 'was', 'were',
    'go', 'come', 'see', 'hear', 'say', 'said', 'tell', 'told', 'speak', 'spoke',
    'give', 'gave', 'take', 'took', 'make', 'made', 'put', 'set', 'bring', 'brought',
    'know', 'knew', 'think', 'thought', 'believe', 'love', 'fear', 'serve',
    'not', 'also', 'even', 'just', 'only', 'still', 'again', 'never', 'always',
    'very', 'most', 'more', 'less', 'too', 'such', 'same', 'other', 'another',
    'first', 'second', 'third', 'last', 'next', 'new', 'old', 'great', 'good',
    'evil', 'holy', 'righteous', 'wicked', 'blessed', 'cursed',
    # Common nouns that might be capitalized
    'lord', 'god', 'king', 'queen', 'prince', 'priest', 'prophet', 'judge',
    'father', 'mother', 'son', 'daughter', 'brother', 'sister', 'wife', 'husband',
    'man', 'woman', 'men', 'women', 'child', 'children', 'people', 'nation',
    'servant', 'master', 'slave', 'elder', 'chief', 'captain', 'commander',
    'spirit', 'soul', 'heart', 'hand', 'eye', 'face', 'voice', 'word', 'name',
    'day', 'night', 'morning', 'evening', 'year', 'month', 'time', 'hour',
    'heaven', 'earth', 'world', 'land', 'sea', 'water', 'fire', 'wind', 'sun', 'moon',
    'house', 'city', 'gate', 'wall', 'temple', 'tabernacle', 'altar', 'ark',
    'mountain', 'hill', 'valley', 'river', 'wilderness', 'desert', 'field',
    'blood', 'bread', 'wine', 'oil', 'gold', 'silver', 'stone', 'wood', 'iron',
    'lamb', 'sheep', 'goat', 'ox', 'bull', 'horse', 'donkey', 'camel', 'lion',
    'offering', 'sacrifice', 'covenant', 'law', 'commandment', 'testimony',
    'glory', 'grace', 'mercy', 'truth', 'peace', 'joy', 'life', 'death',
    'sin', 'iniquity', 'transgression', 'judgment', 'righteousness', 'salvation'
}

def parse_bible(filepath):
    """Parse Bible and extract all capitalized words with chapter context."""
    print(f"Reading {filepath}...")
    content = Path(filepath).read_text(encoding='utf-8')
    
    pattern = re.compile(
        r'^(.+?)\s+--\s+(\d?\s?[a-zA-Z]+(?:\s+of\s+[a-zA-Z]+|\s+[a-zA-Z]+)?)\s+(\d+):(\d+)\s*$',
        re.IGNORECASE
    )
    
    # word -> set of chapters
    word_chapters = defaultdict(set)
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line == '.':
            continue
        
        match = pattern.match(line)
        if match:
            text, book, chapter, verse = match.groups()
            book = book.strip().title()
            chapter_key = f"{book} {chapter}"
            
            # Find capitalized words that are NOT at start of sentence
            # Split into words
            words = re.findall(r'\b[A-Z][a-z]+\b', text)
            
            for word in words:
                word_lower = word.lower()
                # Skip if it's a common word
                if word_lower in COMMON_WORDS_CAPS:
                    continue
                # Skip very short words
                if len(word) < 3:
                    continue
                word_chapters[word_lower].add(chapter_key)
    
    return word_chapters


def main():
    # Extract proper nouns from Bible
    word_chapters = parse_bible("nasb.txt")
    print(f"Found {len(word_chapters)} unique capitalized words")
    
    # Load concordance
    print("Loading concordance...")
    with open("concordance.json", 'r', encoding='utf-8') as f:
        concordance = json.load(f)
    indexed = set(concordance['concordance'].keys())
    
    # Filter to only indexed words
    proper_nouns = {w: chapters for w, chapters in word_chapters.items() if w in indexed}
    print(f"Filtered to {len(proper_nouns)} indexed proper nouns")
    
    # Load existing curated lists for classification
    try:
        with open("entities.json", 'r') as f:
            existing = json.load(f)
        known_people = set(existing.get('people', []))
        known_places = set(existing.get('places', []))
    except:
        known_people = set()
        known_places = set()
    
    # Classify: if in known list, use that; otherwise "unclassified"
    people = {}
    places = {}
    unclassified = {}
    
    for word, chapters in proper_nouns.items():
        count = len(chapters)
        if word in known_people:
            people[word] = count
        elif word in known_places:
            places[word] = count
        else:
            unclassified[word] = count
    
    # Sort all by count
    people_sorted = sorted(people.keys(), key=lambda x: -people[x])
    places_sorted = sorted(places.keys(), key=lambda x: -places[x])
    unclassified_sorted = sorted(unclassified.keys(), key=lambda x: -unclassified[x])
    
    print(f"\nClassified:")
    print(f"  People: {len(people_sorted)}")
    print(f"  Places: {len(places_sorted)}")
    print(f"  Unclassified: {len(unclassified_sorted)}")
    
    # Show unclassified (these need to be added to people or places)
    print(f"\nTop 50 UNCLASSIFIED proper nouns (need categorization):")
    for w in unclassified_sorted[:50]:
        print(f"  {w}: {unclassified[w]} chapters")
    
    # Save all as combined lists for now
    # Add unclassified to people (most genealogical names are people)
    all_people = people_sorted + unclassified_sorted
    all_people_counts = {**people, **unclassified}
    
    output = {
        "people": all_people,
        "places": places_sorted,
        "people_counts": all_people_counts,
        "places_counts": places
    }
    
    with open("entities.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to entities.json")
    print(f"  Total people (including unclassified): {len(all_people)}")
    print(f"  Total places: {len(places_sorted)}")


if __name__ == "__main__":
    main()
