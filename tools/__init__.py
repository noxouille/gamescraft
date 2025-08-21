from typing import Optional, List, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import httpx
import re
from langchain_core.tools import tool


@tool
def get_youtube_transcript(video_url: str) -> Dict[str, Any]:
    """Get transcript from a YouTube video URL."""
    try:
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url)
        if not video_id_match:
            return {"error": "Invalid YouTube URL"}
        
        video_id = video_id_match.group(1)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        full_text = " ".join([entry["text"] for entry in transcript_list])
        
        return {
            "video_id": video_id,
            "transcript": full_text,
            "duration": transcript_list[-1]["start"] if transcript_list else 0,
            "url": video_url
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def scrape_web_content(url: str) -> Dict[str, str]:
    """Scrape content from a web page."""
    try:
        with httpx.Client() as client:
            response = client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            title = soup.find("title")
            title_text = title.string if title else ""
            
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc.get("content", "") if meta_desc else ""
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)
            
            return {
                "title": title_text,
                "description": description,
                "content": text[:5000],
                "url": url
            }
    except Exception as e:
        return {"error": str(e)}


@tool
def search_youtube_videos(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search for YouTube videos related to a query."""
    try:
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        with httpx.Client() as client:
            response = client.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            video_pattern = re.compile(r'/watch\?v=([a-zA-Z0-9_-]{11})')
            video_ids = set(re.findall(video_pattern, response.text))
            
            videos = []
            for video_id in list(video_ids)[:max_results]:
                videos.append({
                    "video_id": video_id,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "title": f"Video {video_id}"
                })
            
            return videos
    except Exception as e:
        return [{"error": str(e)}]


@tool
def search_game_info(game_name: str) -> Dict[str, Any]:
    """Search for game information including release date, genre, and reviews."""
    try:
        search_query = f"{game_name} game review release date"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        with httpx.Client() as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = client.get(search_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            text_content = soup.get_text()[:2000]
            
            return {
                "game_name": game_name,
                "search_results": text_content,
                "query": search_query
            }
    except Exception as e:
        return {"error": str(e), "game_name": game_name}