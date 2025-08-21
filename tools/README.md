# GamesCraft AI Tools

This directory contains modular tools for YouTube gaming content creation, organized by functionality.

## 📁 Module Structure

### `youtube_tools.py`
YouTube-specific functionality for video analysis and discovery.

**Tools:**
- `get_youtube_transcript(video_url)` - Extract video transcripts with multi-language support
- `search_youtube_videos(query, max_results)` - Search YouTube videos with title extraction

**Features:**
- Multi-language transcript support (EN/FR)
- Robust video title extraction using multiple fallback methods
- JSON data parsing from YouTube's internal API

### `web_scraping.py`
General web content extraction and processing.

**Tools:**
- `scrape_web_content(url)` - Extract title, description, and clean text content

**Features:**
- Automatic redirect following
- Content cleaning (removes scripts, styles)
- Meta description extraction
- Error handling for network issues

### `game_research.py`
Specialized tools for gaming content research and analysis.

**Tools:**
- `search_game_info(game_name)` - Wikipedia scraping for comprehensive game data
- `get_game_summary(game_name)` - Content-creator-optimized game summaries

**Features:**
- Wikipedia infobox parsing (release dates, genres, platforms)
- Clean content extraction with citation removal
- Platform recognition and separation
- Known game database with curated information
- Content idea generation for YouTube creators

## 🛠️ Helper Functions

The `game_research.py` module includes several helper functions:

- `_clean_release_date()` - Format Wikipedia release dates
- `_clean_genre()` - Extract primary game genre
- `_clean_platforms()` - Parse and separate gaming platforms
- `_clean_wikipedia_text()` - Remove Wikipedia artifacts and citations

## 📦 Usage

All tools are available through the main `tools` package:

```python
from tools import (
    get_youtube_transcript,
    search_youtube_videos,
    scrape_web_content,
    search_game_info,
    get_game_summary
)

# Example: Get YouTube transcript
result = get_youtube_transcript.invoke({
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID"
})

# Example: Research game information
game_info = search_game_info.invoke({
    "game_name": "Trails in the Sky the 1st"
})
```

## 🧪 Testing

Use the unified test suite to verify all tools:

```bash
# Quick test
uv run python test/test_tools.py --auto

# Interactive testing
uv run python test/test_tools.py
```

## 🔧 Dependencies

- `youtube-transcript-api` - YouTube transcript extraction
- `beautifulsoup4` - HTML parsing and web scraping
- `httpx` - HTTP client for web requests
- `langchain-core` - Tool decorators and interfaces
- `re` - Regular expression processing

## 🚀 Extension Points

To add new tools:

1. Create a new module (e.g., `social_media_tools.py`)
2. Define tools using the `@tool` decorator
3. Add imports to `__init__.py`
4. Update the `__all__` list for proper exports
5. Add test cases to the unified test suite