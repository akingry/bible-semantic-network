"""
Build Concordance Index for Bible Text
Creates a searchable index mapping words to all chapters containing them,
with verse context snippets.

Optimized for speed with batched lemmatization and caching.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

print("Loading spaCy...")

# Use spaCy for lemmatization with caching
import spacy
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

# Lemma cache for speed
LEMMA_CACHE = {}

print("spaCy loaded")

# Common stopwords to exclude
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
    'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have',
    'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
    'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'it', 'its',
    'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they', 'me',
    'him', 'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their', 'mine',
    'yours', 'hers', 'ours', 'theirs', 'who', 'whom', 'which', 'what', 'whose',
    'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
    'most', 'other', 'some', 'any', 'no', 'not', 'only', 'own', 'same', 'so',
    'than', 'too', 'very', 's', 't', 'just', 'don', 'now', 'then', 'there', 'here',
    'also', 'into', 'out', 'up', 'down', 'over', 'under', 'again', 'further',
    'once', 'if', 'because', 'until', 'while', 'about', 'against', 'between',
    'through', 'during', 'before', 'after', 'above', 'below', 'such', 'being',
    'say', 'said', 'tell', 'told', 'go', 'went', 'come', 'came', 'let', 'make',
    'made', 'take', 'took', 'give', 'gave', 'get', 'got', 'put', 'see', 'saw',
    'know', 'knew', 'think', 'thought', 'look', 'looked', 'want', 'wanted',
    'way', 'day', 'man', 'thing', 'time', 'year', 'people', 'son', 'sons'
}


def batch_lemmatize(words):
    """Lemmatize a batch of words efficiently."""
    # Filter out already cached words
    to_process = [w for w in words if w.lower() not in LEMMA_CACHE]
    
    if to_process:
        # Process in batch
        text = " ".join(to_process)
        doc = nlp(text)
        
        # Map each token back
        for token in doc:
            LEMMA_CACHE[token.text.lower()] = token.lemma_.lower()
    
    # Return lemmas for all requested words
    return [LEMMA_CACHE.get(w.lower(), w.lower()) for w in words]


def extract_snippet(verse_text, word, context_chars=60):
    """Extract a snippet around the word occurrence."""
    word_lower = word.lower()
    text_lower = verse_text.lower()
    
    # Find the word
    idx = text_lower.find(word_lower)
    if idx == -1:
        # Try finding any form
        for w in re.findall(r'\b\w+\b', verse_text):
            if LEMMA_CACHE.get(w.lower(), w.lower()) == word_lower:
                idx = text_lower.find(w.lower())
                break
    
    if idx == -1:
        # Word not found - return beginning of text
        return verse_text[:context_chars * 2] + "..." if len(verse_text) > context_chars * 2 else verse_text
    
    # Extract context around word
    start = max(0, idx - context_chars)
    end = min(len(verse_text), idx + len(word) + context_chars)
    
    snippet = verse_text[start:end]
    
    # Add ellipsis if truncated
    if start > 0:
        snippet = "..." + snippet
    if end < len(verse_text):
        snippet = snippet + "..."
    
    return snippet


def parse_bible(filepath):
    """
    Parse NASB Bible text file into chapters with verse-level detail.
    Format: "Text -- book chapter:verse"
    """
    print(f"Reading {filepath}...")
    content = Path(filepath).read_text(encoding='utf-8')
    
    # Pattern for NASB format: "Text -- book chapter:verse"
    pattern = re.compile(
        r'^(.+?)\s+--\s+(\d?\s?[a-zA-Z]+(?:\s+of\s+[a-zA-Z]+|\s+[a-zA-Z]+)?)\s+(\d+):(\d+)\s*$',
        re.IGNORECASE
    )
    
    chapters = defaultdict(lambda: {"full_text": [], "verses": []})
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line == '.':
            continue
        
        match = pattern.match(line)
        if match:
            text, book, chapter, verse = match.groups()
            book = book.strip().title()
            chapter_key = f"{book} {chapter}"
            ref = f"{book} {chapter}:{verse}"
            
            chapters[chapter_key]["full_text"].append(text)
            chapters[chapter_key]["verses"].append({
                "ref": ref,
                "text": text
            })
    
    # Convert full_text lists to strings
    for chapter_key in chapters:
        chapters[chapter_key]["full_text"] = " ".join(chapters[chapter_key]["full_text"])
    
    return dict(chapters)


def build_concordance(bible_filepath, summaries_filepath, output_filepath="concordance.json"):
    """Build the concordance index."""
    
    print("Loading Bible text...")
    chapters = parse_bible(bible_filepath)
    print(f"  Found {len(chapters)} chapters")
    
    print("Loading summaries...")
    with open(summaries_filepath, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    print(f"  Found {len(summaries)} summaries")
    
    print("Building concordance index...")
    
    # First pass: collect ALL unique words for batch lemmatization
    all_words = set()
    total_verses = 0
    
    for chapter_key, chapter_data in chapters.items():
        for verse in chapter_data["verses"]:
            total_verses += 1
            words = re.findall(r'\b[a-zA-Z]+\b', verse["text"])
            all_words.update(w.lower() for w in words if len(w) >= 3)
    
    print(f"  Collected {len(all_words)} unique words from {total_verses} verses")
    
    # Batch lemmatize all words at once
    print("  Lemmatizing words...")
    word_list = list(all_words)
    
    # Process in chunks to avoid memory issues
    chunk_size = 5000
    for i in range(0, len(word_list), chunk_size):
        chunk = word_list[i:i + chunk_size]
        batch_lemmatize(chunk)
        if (i + chunk_size) % 10000 == 0:
            print(f"    Processed {min(i + chunk_size, len(word_list))}/{len(word_list)} words")
    
    print(f"  Lemmatized {len(LEMMA_CACHE)} unique word forms")
    
    # Second pass: build the index
    print("  Building index...")
    
    # chapter -> word -> [verse refs]
    chapter_word_refs = defaultdict(lambda: defaultdict(list))
    
    for idx, (chapter_key, chapter_data) in enumerate(chapters.items()):
        if idx % 200 == 0:
            print(f"    Processing chapter {idx + 1}/{len(chapters)}")
        
        for verse in chapter_data["verses"]:
            ref = verse["ref"]
            text = verse["text"]
            
            # Tokenize and lookup lemmas
            words = re.findall(r'\b[a-zA-Z]+\b', text)
            seen_in_verse = set()
            
            for word in words:
                if len(word) < 3:
                    continue
                
                lemma = LEMMA_CACHE.get(word.lower(), word.lower())
                
                if lemma in STOPWORDS or len(lemma) < 3:
                    continue
                
                if lemma not in seen_in_verse:
                    seen_in_verse.add(lemma)
                    chapter_word_refs[chapter_key][lemma].append({
                        "ref": ref,
                        "text": text
                    })
    
    # Convert to final concordance structure
    print("  Finalizing concordance...")
    concordance = defaultdict(list)
    word_counts = defaultdict(int)
    
    for chapter_key, words_data in chapter_word_refs.items():
        summary = summaries.get(chapter_key, "")
        
        for word, verse_refs in words_data.items():
            word_counts[word] += 1
            
            # Pick the best verse (first occurrence)
            best_verse = verse_refs[0]
            snippet = extract_snippet(best_verse["text"], word)
            
            concordance[word].append({
                "chapter": chapter_key,
                "summary": summary,
                "ref": best_verse["ref"],
                "snippet": snippet,
                "count": len(verse_refs)
            })
    
    # Sort each word's chapters by count (most occurrences first)
    for word in concordance:
        concordance[word].sort(key=lambda x: -x["count"])
    
    print(f"  Indexed {len(concordance)} unique words")
    
    # Build final output structure
    output = {
        "meta": {
            "total_words": len(concordance),
            "total_chapters": len(chapters),
            "total_verses": total_verses
        },
        "concordance": dict(concordance)
    }
    
    # Save
    print(f"Saving to {output_filepath}...")
    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
    
    # Print stats
    print(f"\n{'='*50}")
    print("CONCORDANCE COMPLETE")
    print(f"{'='*50}")
    print(f"  Unique words: {len(concordance):,}")
    print(f"  Chapters: {len(chapters):,}")
    print(f"  Verses: {total_verses:,}")
    
    # Top 20 most common words
    print(f"\nTop 20 most referenced words:")
    sorted_words = sorted(word_counts.items(), key=lambda x: -x[1])[:20]
    for word, count in sorted_words:
        print(f"  {word}: {count} chapters")
    
    print(f"\nSaved to: {output_filepath}")
    
    # File size
    file_size = Path(output_filepath).stat().st_size
    print(f"File size: {file_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    import sys
    
    bible_file = sys.argv[1] if len(sys.argv) > 1 else "nasb.txt"
    summaries_file = sys.argv[2] if len(sys.argv) > 2 else "bible_summaries.json"
    output_file = sys.argv[3] if len(sys.argv) > 3 else "concordance.json"
    
    build_concordance(bible_file, summaries_file, output_file)
