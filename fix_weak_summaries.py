"""
Find and re-summarize weak/generic summaries.
"""

import json
import re
import requests
import time
from pathlib import Path

LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"

# Filler/generic words that indicate weak summaries
FILLER_WORDS = {
    'carefully', 'always', 'slowly', 'quickly', 'greatly', 'fully', 
    'truly', 'really', 'very', 'just', 'simply', 'basically',
    'importantly', 'significantly', 'completely', 'entirely'
}

# Generic verbs that don't convey specific content
GENERIC_PATTERNS = [
    r'\bgives? instructions\b',
    r'\btalks? about\b',
    r'\bdescribes?\b',
    r'\bdiscusses?\b',
    r'\bexplains?\b',
    r'\bcontains?\b',
    r'\bpresents?\b',
    r'\bmentions?\b',
]


def call_llm(chapter_text: str) -> str:
    """Get a specific content summary."""
    payload = {
        "model": "local-model",
        "messages": [
            {
                "role": "system",
                "content": """Summarize in EXACTLY 5 words. Be SPECIFIC about content:
- Name specific people, places, events
- Use concrete nouns and action verbs
- NO filler words (carefully, always, greatly, slowly)
- NO meta descriptions (talks about, discusses, explains)
- Describe WHAT HAPPENS, not what the chapter is about"""
            },
            {
                "role": "user", 
                "content": f"Summarize the actual events/teachings in EXACTLY 5 words:\n\n{chapter_text[:6000]}"
            }
        ],
        "temperature": 0.4,
        "max_tokens": 30
    }
    
    for attempt in range(3):
        try:
            response = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            summary = result["choices"][0]["message"]["content"].strip()
            # Clean up
            summary = summary.strip('"\'.')
            return summary
        except Exception as e:
            print(f"    Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    return None


def is_weak_summary(summary: str) -> tuple[bool, str]:
    """Check if summary is weak/generic. Returns (is_weak, reason)."""
    summary_lower = summary.lower()
    
    # Check for filler words
    for word in FILLER_WORDS:
        if word in summary_lower:
            return True, f"filler word: '{word}'"
    
    # Check for generic patterns
    for pattern in GENERIC_PATTERNS:
        if re.search(pattern, summary_lower):
            return True, f"generic pattern"
    
    # Check for meta words
    meta_words = ['bible', 'chapter', 'verse', 'passage', 'scripture', 'text']
    for word in meta_words:
        if word in summary_lower:
            return True, f"meta word: '{word}'"
    
    return False, ""


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


def fix_specific_chapters(chapters_to_fix: list, summaries: dict, bible_chapters: dict) -> int:
    """Fix specific chapters by name."""
    fixed = 0
    for chapter in chapters_to_fix:
        if chapter not in summaries:
            print(f"  {chapter} - NOT FOUND in summaries")
            continue
        
        old_summary = summaries[chapter]
        print(f"\n  {chapter}")
        print(f"    Old: {old_summary}")
        
        if chapter not in bible_chapters:
            print(f"    ERROR: Chapter not in Bible text")
            continue
        
        new_summary = call_llm(bible_chapters[chapter])
        
        if new_summary:
            print(f"    New: {new_summary}")
            summaries[chapter] = new_summary
            fixed += 1
        else:
            print(f"    FAILED")
    
    return fixed


def scan_and_fix_weak(summaries: dict, bible_chapters: dict, limit: int = None) -> int:
    """Scan all summaries and fix weak ones."""
    weak_chapters = []
    
    print("\nScanning for weak summaries...")
    for chapter, summary in summaries.items():
        is_weak, reason = is_weak_summary(summary)
        if is_weak:
            weak_chapters.append((chapter, summary, reason))
    
    print(f"Found {len(weak_chapters)} weak summaries")
    
    if not weak_chapters:
        return 0
    
    # Show them
    print("\nWeak summaries found:")
    for chapter, summary, reason in weak_chapters[:20]:
        print(f"  {chapter}: \"{summary}\" ({reason})")
    
    if len(weak_chapters) > 20:
        print(f"  ... and {len(weak_chapters) - 20} more")
    
    # Ask to continue
    if limit:
        to_fix = weak_chapters[:limit]
    else:
        to_fix = weak_chapters
    
    print(f"\nFixing {len(to_fix)} summaries...")
    
    fixed = 0
    for i, (chapter, old_summary, reason) in enumerate(to_fix, 1):
        print(f"\n[{i}/{len(to_fix)}] {chapter}")
        print(f"  Old: {old_summary} ({reason})")
        
        if chapter not in bible_chapters:
            print(f"  ERROR: Not in Bible text")
            continue
        
        new_summary = call_llm(bible_chapters[chapter])
        
        if new_summary:
            # Check if new one is also weak
            still_weak, _ = is_weak_summary(new_summary)
            if still_weak:
                print(f"  New (still weak): {new_summary}")
            else:
                print(f"  New: {new_summary}")
            summaries[chapter] = new_summary
            fixed += 1
        else:
            print(f"  FAILED")
    
    return fixed


def main():
    import sys
    
    summaries_file = Path("bible_summaries.json")
    bible_file = Path("nasb.txt")
    
    print("Loading summaries...")
    with open(summaries_file) as f:
        summaries = json.load(f)
    
    print("Loading Bible text...")
    bible_chapters = parse_bible_text(bible_file)
    
    # Check LM Studio
    try:
        requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
        print("Connected to LM Studio\n")
    except:
        print("ERROR: Cannot connect to LM Studio at port 1234")
        print("Make sure LM Studio is running with a model loaded.")
        return
    
    # Check for specific chapter argument
    if len(sys.argv) > 1:
        # Fix specific chapters
        chapters_to_fix = sys.argv[1:]
        print(f"Fixing specific chapters: {chapters_to_fix}")
        fixed = fix_specific_chapters(chapters_to_fix, summaries, bible_chapters)
    else:
        # Scan and fix weak summaries
        fixed = scan_and_fix_weak(summaries, bible_chapters, limit=50)
    
    if fixed > 0:
        print(f"\n\nSaving {fixed} updated summaries...")
        with open(summaries_file, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, indent=2, ensure_ascii=False)
        print(f"Saved to {summaries_file}")
        
        # Also need to rebuild concordance and network
        print("\nNOTE: Run build_concordance.py and build_network.py to update indexes.")


if __name__ == "__main__":
    main()
