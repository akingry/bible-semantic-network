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

### Concordance Mode (Proposed)
A **separate search mode** that searches the actual Bible text, not just summaries.

**Purpose:** Find ALL chapters mentioning a specific word (e.g., "pharisee" → 23+ chapters)

**Implementation:**
```python
# No LLM needed - just text indexing
concordance = {}  # word → [chapters]

for chapter, text in bible_chapters.items():
    for word in text.split():
        lemma = lemmatize(word.lower())
        if lemma not in stopwords and len(lemma) > 2:
            concordance[lemma].append({
                'chapter': chapter,
                'context': extract_snippet(text, word)  # surrounding text
            })

# Save to concordance.json
```

**UI Design:**
- Tab or toggle: `[Network Mode] [Concordance Mode]`
- Search box in Concordance mode searches actual Bible text
- Results show:
  - Chapter name
  - 5-word summary (from existing data)
  - Verse snippet with search term highlighted
- Paginated list (not a graph)
- Click chapter → could switch to Network mode filtered to that book

**Effort estimate:** 2-3 hours

**Files to create:**
- `build_concordance.py` - Index builder
- `concordance.json` - Word → chapters index with snippets
- Update `visualization.html` - Add Concordance tab/mode

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
