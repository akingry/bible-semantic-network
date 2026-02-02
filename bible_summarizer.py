"""
Bible Chapter Summarizer using Local LLM (LM Studio)
Summarizes each chapter of the Bible in exactly 5 words.
"""

import json
import re
import time
from pathlib import Path
from datetime import datetime, timedelta
import requests

# LM Studio API endpoint
LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"

# Progress tracking
class ProgressTracker:
    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.start_time = time.time()
        self.chapter_times = []
    
    def update(self, chapter_name: str, summary: str, chapter_len: int):
        self.completed += 1
        elapsed = time.time() - self.start_time
        self.chapter_times.append(elapsed / self.completed)
        
        # Calculate stats
        avg_time = sum(self.chapter_times[-20:]) / len(self.chapter_times[-20:])  # Rolling avg
        remaining = self.total - self.completed
        eta_seconds = remaining * avg_time
        eta = timedelta(seconds=int(eta_seconds))
        elapsed_fmt = timedelta(seconds=int(elapsed))
        pct = (self.completed / self.total) * 100
        
        # Progress bar
        bar_width = 30
        filled = int(bar_width * self.completed / self.total)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        # Print verbose output
        print(f"\n{'='*60}")
        print(f"[{self.completed}/{self.total}] {chapter_name}")
        print(f"{'='*60}")
        print(f"  Chapter length: {chapter_len:,} characters")
        print(f"  Summary: \"{summary}\"")
        print(f"  Progress: [{bar}] {pct:.1f}%")
        print(f"  Elapsed: {elapsed_fmt} | ETA: {eta} | Avg: {avg_time:.1f}s/chapter")
        
    def print_final_stats(self):
        elapsed = time.time() - self.start_time
        elapsed_fmt = timedelta(seconds=int(elapsed))
        avg = elapsed / self.completed if self.completed > 0 else 0
        print(f"\n{'='*60}")
        print(f"COMPLETED")
        print(f"{'='*60}")
        print(f"  Total chapters: {self.completed}")
        print(f"  Total time: {elapsed_fmt}")
        print(f"  Average per chapter: {avg:.1f} seconds")
        print(f"{'='*60}\n")

def call_llm(prompt: str, max_retries: int = 3, verbose: bool = True) -> str:
    """Send prompt to LM Studio and get response."""
    payload = {
        "model": "local-model",  # LM Studio ignores this, uses loaded model
        "messages": [
            {
                "role": "system",
                "content": "You are a precise summarizer. You MUST respond with EXACTLY 5 words. No more, no less. No punctuation at the end."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 30
    }
    
    for attempt in range(max_retries):
        try:
            start = time.time()
            response = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            llm_time = time.time() - start
            
            content = result["choices"][0]["message"]["content"].strip()
            
            if verbose:
                tokens_used = result.get("usage", {})
                prompt_tokens = tokens_used.get("prompt_tokens", "?")
                completion_tokens = tokens_used.get("completion_tokens", "?")
                print(f"  LLM response time: {llm_time:.1f}s | Tokens: {prompt_tokens} in / {completion_tokens} out")
            
            return content
        except requests.exceptions.RequestException as e:
            print(f"  ⚠ Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in 2 seconds...")
                time.sleep(2)
    return "ERROR: Failed to get response"


def parse_bible_text(filepath: Path) -> dict:
    """
    Parse Bible text file into chapters.
    
    Expected format (one of):
    1. Lines starting with "Book Chapter:Verse" (e.g., "Genesis 1:1 In the beginning...")
    2. Headers like "Genesis Chapter 1" followed by text
    3. JSON with structure: {"books": [{"name": "Genesis", "chapters": [{"chapter": 1, "text": "..."}]}]}
    """
    content = filepath.read_text(encoding='utf-8')
    
    # Check if JSON
    if filepath.suffix.lower() == '.json':
        return parse_json_bible(json.loads(content))
    
    # Parse text format
    return parse_text_bible(content)


def parse_json_bible(data: dict) -> dict:
    """Parse JSON formatted Bible."""
    chapters = {}
    
    # Handle various JSON structures
    if "books" in data:
        for book in data["books"]:
            book_name = book.get("name") or book.get("book")
            for ch in book.get("chapters", []):
                ch_num = ch.get("chapter") or ch.get("number")
                text = ch.get("text") or ch.get("content")
                if isinstance(text, list):
                    # Verses as list
                    text = " ".join(v.get("text", str(v)) for v in text)
                key = f"{book_name} {ch_num}"
                chapters[key] = text
    
    # Alternative: flat structure {"Genesis 1": "text", ...}
    elif all(isinstance(v, str) for v in data.values()):
        chapters = data
    
    return chapters


def parse_text_bible(content: str) -> dict:
    """Parse plain text Bible with book/chapter markers."""
    chapters = {}
    current_book = ""
    current_chapter = ""
    current_text = []
    
    # Pattern for "Text -- book chapter:verse" format (NASB style)
    # Book names can be: genesis, 1 samuel, 2 kings, song of solomon, etc.
    nasb_pattern = re.compile(r'^(.+?)\s+--\s+(\d?\s?[a-zA-Z]+(?:\s+of\s+[a-zA-Z]+|\s+[a-zA-Z]+)?)\s+(\d+):(\d+)\s*$', re.IGNORECASE)
    # Pattern for "Book Chapter:Verse Text" format (standard)
    standard_pattern = re.compile(r'^(\d?\s?[A-Za-z]+)\s+(\d+):(\d+)\s+(.+)$')
    # Pattern for chapter headers
    chapter_header = re.compile(r'^((?:\d\s)?[A-Za-z]+)\s+(?:Chapter\s+)?(\d+)\s*$', re.IGNORECASE)
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line == '.':
            continue
        
        # Check for NASB format: "Text -- book chapter:verse"
        nasb_match = nasb_pattern.match(line)
        if nasb_match:
            text, book, chapter, verse = nasb_match.groups()
            # Capitalize book name properly
            book = book.strip().title()
            
            # New chapter?
            if book != current_book or chapter != current_chapter:
                # Save previous
                if current_book and current_chapter and current_text:
                    key = f"{current_book} {current_chapter}"
                    chapters[key] = " ".join(current_text)
                
                current_book = book
                current_chapter = chapter
                current_text = []
            
            current_text.append(text)
            continue
        
        # Check for chapter header
        header_match = chapter_header.match(line)
        if header_match:
            # Save previous chapter
            if current_book and current_chapter and current_text:
                key = f"{current_book} {current_chapter}"
                chapters[key] = " ".join(current_text)
            
            current_book = header_match.group(1)
            current_chapter = header_match.group(2)
            current_text = []
            continue
        
        # Check for standard verse format
        standard_match = standard_pattern.match(line)
        if standard_match:
            book, chapter, verse, text = standard_match.groups()
            
            # New chapter?
            if book != current_book or chapter != current_chapter:
                # Save previous
                if current_book and current_chapter and current_text:
                    key = f"{current_book} {current_chapter}"
                    chapters[key] = " ".join(current_text)
                
                current_book = book
                current_chapter = chapter
                current_text = []
            
            current_text.append(text)
        else:
            # Continuation of current chapter
            if current_book and current_chapter:
                current_text.append(line)
    
    # Don't forget last chapter
    if current_book and current_chapter and current_text:
        key = f"{current_book} {current_chapter}"
        chapters[key] = " ".join(current_text)
    
    return chapters


def summarize_bible(input_file: str, output_file: str = "bible_summaries.json"):
    """Main function to summarize all Bible chapters."""
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: File not found: {input_file}")
        return
    
    print(f"Loading Bible from: {input_file}")
    chapters = parse_bible_text(input_path)
    
    if not chapters:
        print("Error: Could not parse any chapters from the file.")
        print("Expected formats:")
        print("  - NASB: 'In the beginning... -- genesis 1:1'")
        print("  - Standard: 'Genesis 1:1 In the beginning...'")
        print("  - JSON structure")
        return
    
    # Show what books were found
    books_found = sorted(set(ch.rsplit(' ', 1)[0] for ch in chapters.keys()))
    print(f"\nBooks detected ({len(books_found)}): {', '.join(books_found[:10])}{'...' if len(books_found) > 10 else ''}")
    
    print(f"Found {len(chapters)} chapters to summarize")
    
    # Check LM Studio connection
    try:
        requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
        print("Connected to LM Studio")
    except:
        print("Error: Cannot connect to LM Studio at http://127.0.0.1:1234")
        print("Make sure LM Studio is running with a model loaded.")
        return
    
    summaries = {}
    total = len(chapters)
    tracker = ProgressTracker(total)
    
    print(f"\n{'='*60}")
    print(f"BIBLE SUMMARIZER - Starting")
    print(f"{'='*60}")
    print(f"  Input file: {input_file}")
    print(f"  Output file: {output_file}")
    print(f"  Chapters to process: {total}")
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Sort chapters in Bible order (approximately)
    bible_order = [
        "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
        "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", 
        "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
        "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
        "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah",
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
    
    def sort_key(chapter_name):
        parts = chapter_name.rsplit(' ', 1)
        book = parts[0]
        ch_num = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        try:
            book_idx = bible_order.index(book)
        except ValueError:
            book_idx = 999
        return (book_idx, ch_num)
    
    sorted_chapters = sorted(chapters.keys(), key=sort_key)
    
    for i, chapter_name in enumerate(sorted_chapters, 1):
        chapter_text = chapters[chapter_name]
        original_len = len(chapter_text)
        
        # Truncate very long chapters to avoid context issues
        if len(chapter_text) > 8000:
            chapter_text = chapter_text[:8000] + "..."
        
        prompt = f"Summarize this Bible chapter in EXACTLY 5 words:\n\n{chapter_text}"
        
        summary = call_llm(prompt)
        summaries[chapter_name] = summary
        
        # Update progress tracker with verbose output
        tracker.update(chapter_name, summary, original_len)
        
        # Save progress every 10 chapters
        if i % 10 == 0:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summaries, f, indent=2, ensure_ascii=False)
            print(f"  [Checkpoint saved to {output_file}]")
    
    # Final save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    
    tracker.print_final_stats()
    print(f"Summaries saved to: {output_file}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Bible Chapter Summarizer")
        print("=" * 40)
        print("\nUsage: python bible_summarizer.py <bible_file.txt|json> [output.json]")
        print("\nExpected input formats:")
        print("  1. Text: 'Genesis 1:1 In the beginning God created...'")
        print("  2. JSON: {'books': [{'name': 'Genesis', 'chapters': [...]}]}")
        print("\nMake sure LM Studio is running with Llama 3.1 8B loaded.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "bible_summaries.json"
    
    summarize_bible(input_file, output_file)
