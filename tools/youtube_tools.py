"""
YouTube-related tools for GamesCraft AI system.
Handles video transcript extraction and video search functionality.
"""

from typing import Dict, List, Any
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import httpx
import re
import json
from langchain_core.tools import tool


@tool
def get_youtube_transcript(video_url: str) -> Dict[str, Any]:
    """Get transcript from a YouTube video URL."""
    try:
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url)
        if not video_id_match:
            return {"error": "Invalid YouTube URL"}
        
        video_id = video_id_match.group(1)
        
        # Try to get transcript in multiple languages
        try:
            transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=['en', 'fr'])
        except:
            # If specific languages fail, try getting any available transcript
            transcript_list = YouTubeTranscriptApi().fetch(video_id)
        
        # Handle the new API format
        full_text = " ".join([entry.text for entry in transcript_list])
        
        return {
            "video_id": video_id,
            "transcript": full_text,
            "duration": transcript_list[-1].start + transcript_list[-1].duration if transcript_list else 0,
            "url": video_url
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def search_youtube_videos(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search for YouTube videos related to a query."""
    try:
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        with httpx.Client() as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = client.get(search_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            videos = []
            
            # Method 1: Try to find JSON data with video information
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'var ytInitialData' in script.string:
                    try:
                        # Extract JSON data from script tag
                        json_str = script.string.split('var ytInitialData = ')[1].split(';</script>')[0]
                        json_str = json_str.rstrip(';')
                        data = json.loads(json_str)
                        
                        # Navigate through YouTube's data structure
                        contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
                        
                        for section in contents:
                            if 'itemSectionRenderer' in section:
                                items = section['itemSectionRenderer'].get('contents', [])
                                for item in items:
                                    if 'videoRenderer' in item:
                                        video = item['videoRenderer']
                                        video_id = video.get('videoId', '')
                                        title_runs = video.get('title', {}).get('runs', [])
                                        title = title_runs[0].get('text', f'Video {video_id}') if title_runs else f'Video {video_id}'
                                        
                                        if video_id and len(videos) < max_results:
                                            videos.append({
                                                "video_id": video_id,
                                                "url": f"https://www.youtube.com/watch?v={video_id}",
                                                "title": title[:100]  # Limit title length
                                            })
                        break
                    except Exception:
                        continue
            
            # Method 2: Fallback to basic scraping if JSON parsing fails
            if not videos:
                # Look for video containers with titles
                video_elements = soup.find_all('a', {'id': 'video-title'}) or soup.find_all('a', href=re.compile(r'/watch\?v='))
                
                for element in video_elements[:max_results]:
                    href = element.get('href', '')
                    title = element.get('title') or element.get_text().strip()
                    
                    video_id_match = re.search(r'/watch\?v=([a-zA-Z0-9_-]{11})', href)
                    if video_id_match:
                        video_id = video_id_match.group(1)
                        if title and title.strip():
                            videos.append({
                                "video_id": video_id,
                                "url": f"https://www.youtube.com/watch?v={video_id}",
                                "title": title.strip()[:100]
                            })
            
            # Method 3: Final fallback - just get video IDs with placeholder titles
            if not videos:
                video_pattern = re.compile(r'/watch\?v=([a-zA-Z0-9_-]{11})')
                video_ids = set(re.findall(video_pattern, response.text))
                
                for video_id in list(video_ids)[:max_results]:
                    videos.append({
                        "video_id": video_id,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "title": f"Video {video_id} (title not available)"
                    })
            
            return videos[:max_results]
            
    except Exception as e:
        return [{"error": str(e)}]