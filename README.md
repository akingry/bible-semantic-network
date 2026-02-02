# 📖 Bible Semantic Network

An interactive visualization for exploring the Bible through semantic relationships and full-text search.

## Features

### 🕸️ Network View
Explore Bible chapters through a force-directed graph of semantic relationships:
- **Subjects** (orange) → **Verbs** (purple) → **Objects** (green) → **Chapters** (red)
- Each chapter is summarized in 5 words using AI
- Click nodes to drill down through concept chains
- Filter by book, search for specific terms

### 📚 Concordance View
Full-text search across all 31,102 verses:
- Find every chapter containing a word
- See verse context with highlighted matches
- Browse popular words sidebar

### 📖 Chapter Reader
Kindle-style reading experience:
- Clean typography with adjustable font size
- Previous/Next navigation with keyboard shortcuts
- Jump to any book and chapter directly

### 🔊 Voice Reader
Listen to chapters read aloud:
- Text-to-speech with streaming playback
- Starts playing within seconds
- Pause/resume support

## Live Demo

**[View the Bible Semantic Network](https://akingry.github.io/bible-semantic-network/)**

## Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/akingry/bible-semantic-network.git
   cd bible-semantic-network
   ```

2. Install dependencies (for TTS):
   ```bash
   pip install edge-tts aiohttp
   ```

3. Start the server:
   ```bash
   python server.py
   ```
   
   Or use the batch file:
   ```bash
   run_visualization.bat
   ```

4. Open the URL shown in the terminal (auto-opens browser)

## Tech Stack

- **D3.js** — Force-directed graph visualization
- **spaCy** — NLP parsing for semantic extraction
- **Edge TTS** — Microsoft's free text-to-speech API
- **aiohttp** — Async HTTP server for streaming audio
- **Vanilla JS/CSS** — No framework dependencies

## Data

- **1,189 chapters** with AI-generated 5-word summaries
- **31,102 verses** indexed for concordance search
- **~2,400 semantic nodes** (subjects, verbs, objects)
- Bible text: NASB (New American Standard Bible)

## Building from Source

See [BUILD.md](BUILD.md) for detailed instructions on:
- Generating chapter summaries with local LLM
- Building the semantic network
- Creating the concordance index

## License

MIT License — See [LICENSE](LICENSE) for details.

## Author

Created by Adam Kingry
