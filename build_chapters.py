"""
Build Chapters JSON for Reader View
Exports full chapter text organized for easy navigation.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Bible book order for navigation
BIBLE_ORDER = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
    "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "Song Of Solomon", "Isaiah", "Jeremiah",
    "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
    "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
    "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
    "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
    "Jude", "Revelation"
]


def parse_bible(filepath):
    """Parse NASB Bible into chapters with verses."""
    print(f"Reading {filepath}...")
    content = Path(filepath).read_text(encoding='utf-8')
    
    # Pattern: "Text -- book chapter:verse"
    pattern = re.compile(
        r'^(.+?)\s+--\s+(\d?\s?[a-zA-Z]+(?:\s+of\s+[a-zA-Z]+|\s+[a-zA-Z]+)?)\s+(\d+):(\d+)\s*$',
        re.IGNORECASE
    )
    
    chapters = defaultdict(lambda: {"book": "", "chapter": 0, "verses": []})
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line == '.':
            continue
        
        match = pattern.match(line)
        if match:
            text, book, chapter, verse = match.groups()
            book = book.strip().title()
            chapter_num = int(chapter)
            verse_num = int(verse)
            chapter_key = f"{book} {chapter}"
            
            chapters[chapter_key]["book"] = book
            chapters[chapter_key]["chapter"] = chapter_num
            chapters[chapter_key]["verses"].append({
                "verse": verse_num,
                "text": text
            })
    
    return dict(chapters)


def build_chapters_json(bible_filepath, summaries_filepath, output_filepath="chapters.json"):
    """Build the chapters JSON with navigation info."""
    
    print("Loading Bible text...")
    chapters = parse_bible(bible_filepath)
    print(f"  Found {len(chapters)} chapters")
    
    print("Loading summaries...")
    with open(summaries_filepath, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    
    # Build ordered list of all chapters
    all_chapters = []
    for book in BIBLE_ORDER:
        book_chapters = [(k, v) for k, v in chapters.items() if v["book"] == book]
        book_chapters.sort(key=lambda x: x[1]["chapter"])
        all_chapters.extend(book_chapters)
    
    print(f"  Ordered {len(all_chapters)} chapters")
    
    # Build output with navigation
    output = {
        "meta": {
            "total_chapters": len(all_chapters),
            "books": BIBLE_ORDER
        },
        "order": [ch[0] for ch in all_chapters],  # Ordered list of chapter keys
        "chapters": {}
    }
    
    for i, (chapter_key, chapter_data) in enumerate(all_chapters):
        prev_chapter = all_chapters[i - 1][0] if i > 0 else None
        next_chapter = all_chapters[i + 1][0] if i < len(all_chapters) - 1 else None
        
        output["chapters"][chapter_key] = {
            "book": chapter_data["book"],
            "chapter": chapter_data["chapter"],
            "summary": summaries.get(chapter_key, ""),
            "verses": chapter_data["verses"],
            "prev": prev_chapter,
            "next": next_chapter
        }
    
    # Save
    print(f"Saving to {output_filepath}...")
    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
    
    file_size = Path(output_filepath).stat().st_size
    print(f"\nDone! {len(all_chapters)} chapters saved ({file_size / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    import sys
    
    bible_file = sys.argv[1] if len(sys.argv) > 1 else "nasb.txt"
    summaries_file = sys.argv[2] if len(sys.argv) > 2 else "bible_summaries.json"
    output_file = sys.argv[3] if len(sys.argv) > 3 else "chapters.json"
    
    build_chapters_json(bible_file, summaries_file, output_file)
