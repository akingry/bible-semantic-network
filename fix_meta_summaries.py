"""
Re-summarize chapters that have generic/meta summaries.
"""

import json
import re
import requests
import time
from pathlib import Path

LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"

def call_llm(chapter_text: str) -> str:
    """Get a proper content summary, not a meta description."""
    payload = {
        "model": "local-model",
        "messages": [
            {
                "role": "system",
                "content": "Summarize the EVENTS or TEACHINGS in exactly 5 words. Do NOT say 'Bible', 'chapter', 'verse', 'passage', 'scripture', or 'text'. Describe WHAT HAPPENS or WHAT IS TAUGHT, not what the chapter is about."
            },
            {
                "role": "user", 
                "content": f"Summarize the actual content in EXACTLY 5 words:\n\n{chapter_text}"
            }
        ],
        "temperature": 0.5,
        "max_tokens": 30
    }
    
    for attempt in range(3):
        try:
            response = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            summary = result["choices"][0]["message"]["content"].strip()
            
            # Check if still meta
            meta_words = ['bible', 'chapter', 'verse', 'passage', 'scripture', 'text']
            if any(w in summary.lower() for w in meta_words):
                print(f"    Still meta, retrying...")
                continue
            return summary
        except Exception as e:
            print(f"    Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    return None


def parse_bible_text(filepath: Path) -> dict:
    """Parse Bible into chapters."""
    content = filepath.read_text(encoding='utf-8')
    chapters = {}
    current_book = ""
    current_chapter = ""
    current_text = []
    
    nasb_pattern = re.compile(r'^(.+?)\s+--\s+(\d?\s?[a-zA-Z]+(?:\s+of\s+[a-zA-Z]+|\s+[a-zA-Z]+)?)\s+(\d+):(\d+)\s*$', re.IGNORECASE)
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line == '.':
            continue
        
        nasb_match = nasb_pattern.match(line)
        if nasb_match:
            text, book, chapter, verse = nasb_match.groups()
            book = book.strip().title()
            
            if book != current_book or chapter != current_chapter:
                if current_book and current_chapter and current_text:
                    key = f"{current_book} {current_chapter}"
                    chapters[key] = " ".join(current_text)
                
                current_book = book
                current_chapter = chapter
                current_text = []
            
            current_text.append(text)
    
    if current_book and current_chapter and current_text:
        key = f"{current_book} {current_chapter}"
        chapters[key] = " ".join(current_text)
    
    return chapters


def main():
    summaries_file = Path("bible_summaries.json")
    bible_file = Path("nasb.txt")
    
    with open(summaries_file) as f:
        summaries = json.load(f)
    
    # Find meta summaries
    meta_words = ['bible', 'chapter', 'verse', 'passage', 'scripture', 'text']
    bad_chapters = [k for k, v in summaries.items() 
                    if any(w in v.lower() for w in meta_words)]
    
    print(f"Found {len(bad_chapters)} meta summaries to fix")
    
    if not bad_chapters:
        print("Nothing to fix!")
        return
    
    # Parse Bible
    print("Loading Bible text...")
    bible_chapters = parse_bible_text(bible_file)
    
    # Check LM Studio
    try:
        requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
        print("Connected to LM Studio")
    except:
        print("Error: Cannot connect to LM Studio. Make sure it's running.")
        return
    
    # Re-summarize
    for i, chapter in enumerate(bad_chapters, 1):
        old_summary = summaries[chapter]
        print(f"\n[{i}/{len(bad_chapters)}] {chapter}")
        print(f"  Old: {old_summary}")
        
        if chapter not in bible_chapters:
            print(f"  ERROR: Chapter not found in Bible text")
            continue
        
        chapter_text = bible_chapters[chapter]
        if len(chapter_text) > 8000:
            chapter_text = chapter_text[:8000] + "..."
        
        new_summary = call_llm(chapter_text)
        
        if new_summary:
            print(f"  New: {new_summary}")
            summaries[chapter] = new_summary
        else:
            print(f"  FAILED - keeping old summary")
    
    # Save
    with open(summaries_file, 'w', encoding='utf-8') as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Updated {summaries_file}")


if __name__ == "__main__":
    main()
