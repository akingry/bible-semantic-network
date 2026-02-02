# Bible Semantic Network - Build Documentation

## Project Overview

An interactive visualization of Bible chapter summaries as a semantic network. Each chapter is summarized in 5 words using a local LLM (Llama 3.1 8B via LM Studio), then parsed with spaCy NLP to extract subjects, verbs, and objects. The result is a navigable network where you can explore chains of concepts leading to Bible chapters.

**Example chain:** `God → warn → impending → doom → Jeremiah 4`

## Current State (Completed)

### 1. Bible Summarizer (`bible_summarizer.py`)
- Parses NASB Bible text file (verse format: `Text -- book chapter:verse`)
- Sends each chapter to LM Studio's local API
- Gets 5-word summaries
- Shows verbose progress (ETA, tokens, etc.)
- Saves to `bible_summaries.json`

### 2. Network Builder (`build_network.py`)
- Uses spaCy NLP to parse summaries
- Extracts semantic roles:
  - **Subjects** (actors): God, Jesus, Moses, David, etc.
  - **Verbs** (actions): warn, teach, speak, love, give, etc.
  - **Objects**: covenant, law, glory, etc.
  - **Modifiers**: great, holy, eternal, etc.
- Lemmatizes words (men→man, kings→king, warns→warn)
- Builds chain links: Subject → Verb → Object → Chapter
- Stores each chapter's word chain for path validation
- Outputs `network_data.json`

### 3. Visualization (`visualization.html`)
Interactive D3.js force-directed graph with:

**Node Types (color-coded):**
- 🟠 Orange = Subjects (actors)
- 🟣 Purple = Verbs (actions)
- 🟢 Green = Objects
- 🔵 Blue = Modifiers
- 🔴 Red = Chapters (leaf nodes)

**Navigation:**
- Click node to start/continue chain
- Only shows valid next nodes (chapters must contain ALL words in path)
- Click same node or press `Backspace` to go back one step
- Press `Esc` or right-click to reset
- Touch-friendly Back/Reset buttons for mobile

**Features:**
- Search box → zooms and centers on node
- Filter by book (dropdown in Bible order)
- Active Nodes panel (right side) → clickable list of visible nodes
- Path nodes shown dimmed in panel (already clicked)
- Tooltips show word usage count and chapter summaries

**Book filtering:**
- Only shows words that ACTUALLY appear in selected book's chapter chains
- Rebuilds links from actual chains, not global graph

### 4. Helper Scripts
- `server.py` - Simple HTTP server, auto-finds open port
- `run_visualization.bat` - One-click launcher
- `run_summarizer.bat` - One-click summarizer
- `fix_meta_summaries.py` - Re-summarizes generic/meta summaries

### 5. Data Files
- `nasb.txt` - NASB Bible text (user-provided, copyrighted)
- `bible_summaries.json` - 1,189 chapter summaries (5 words each)
- `network_data.json` - Nodes, links, and chapter chains

## Known Issues / Limitations

1. **5-word summaries can't capture everything** - A chapter mentioning Pharisees 10 times might not have "pharisee" in its 5-word summary. This limits discoverability.

2. **Some summaries may still be imperfect** - LLM occasionally produces odd phrasings or misses key content.

3. **Large network performance** - With ~2,400 nodes, initial render can be slow on older devices.

## What's Left to Build

### ~~Concordance Mode~~ ✅ COMPLETED (2026-02-02)
Full-text search mode that searches actual Bible text (not just summaries).

**Files created:**
- `build_concordance.py` - Indexes all 31,102 verses with spaCy lemmatization
- `concordance.json` - 10,001 unique words mapped to chapters with verse snippets (34 MB)
- Updated `visualization.html` - Added Concordance tab with search and results

**Features:**
- Tab toggle between Network and Concordance modes
- Search any word to find ALL chapters containing it
- Results show: chapter name, 5-word summary, highlighted verse snippet
- Popular words sidebar for quick browsing
- Occurrence counts per chapter

### ~~Chapter Reader~~ ✅ COMPLETED (2026-02-02)
Kindle-style reader for reading full chapter text with navigation.

**Files created:**
- `build_chapters.py` - Exports all chapter text with verse numbers and navigation links
- `chapters.json` - 1,189 chapters with full text, summaries, and prev/next links (4.84 MB)
- Updated `visualization.html` - Added reader modal overlay

**Features:**
- Clean, readable typography (Georgia serif font)
- Verse numbers styled subtly
- Summary shown in header
- Previous/Next chapter navigation (arrows or buttons)
- Seamless book transitions (e.g., Genesis 50 → Exodus 1)
- Keyboard shortcuts: ←/→ navigate, Esc closes
- Opens from: double-click chapter in Network, click chapter in Concordance

### Other Potential Enhancements

1. **Verse-level summaries** - 31,000 verses instead of 1,189 chapters (35+ hours LLM time, needs UI pagination)

2. **Semantic search** - "religious leaders" finds Pharisees, Sadducees, scribes (would need embeddings)

3. **Cross-references** - Link related chapters (e.g., Gospel parallels)

4. **Export** - Save current path/selection as shareable link or image

## Tech Stack

- **Python 3.12**
- **spaCy** (en_core_web_sm) - NLP parsing
- **LM Studio** - Local LLM API (OpenAI-compatible)
- **Llama 3.1 8B** (Q4_K_M) - Summarization model
- **D3.js v7** - Force-directed graph visualization
- **Vanilla HTML/CSS/JS** - No framework dependencies

## How to Run

1. **Summarize Bible** (if not already done):
   - Start LM Studio with Llama 3.1 8B loaded
   - Run `run_summarizer.bat`
   - Takes ~1-2 hours for all 1,189 chapters

2. **Build Network** (if summaries changed):
   ```
   python build_network.py
   ```

3. **View Visualization:**
   ```
   run_visualization.bat
   ```
   Or manually: `python server.py`

## Repository

Private GitHub repo: https://github.com/akingry/bible-semantic-network
