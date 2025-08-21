from typing import Optional, List, Dict, Any
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


@tool
def search_game_info(game_name: str) -> Dict[str, Any]:
    """Search for game information including release date, genre, and reviews."""
    try:
        game_info = {
            "game_name": game_name,
            "sources": [],
            "description": "",
            "release_date": "",
            "genre": "",
            "platforms": []
        }
        
        with httpx.Client() as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # Try Wikipedia with simplified but robust parsing
            wiki_url = f"https://en.wikipedia.org/wiki/{game_name.replace(' ', '_')}"
            try:
                response = client.get(wiki_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    content_parts = []
                    
                    # Simple approach: get first few substantial paragraphs
                    all_paragraphs = soup.find_all('p')
                    
                    for i, para in enumerate(all_paragraphs[:10]):
                        text = para.get_text().strip()
                        
                        # Skip very short paragraphs
                        if len(text) < 80:
                            continue
                        
                        # Skip disambiguation and metadata paragraphs
                        if any(skip in text.lower() for skip in [
                            'may refer to', 'disambiguation', 'coordinates',
                            'this article is about', 'for other uses'
                        ]):
                            continue
                        
                        # Clean the text
                        cleaned_text = _clean_wikipedia_text(text)
                        
                        if len(cleaned_text) > 100:
                            content_parts.append(cleaned_text)
                            break  # Just get the first good paragraph
                    
                    # Try to extract from infobox with better parsing
                    infobox = soup.find('table', {'class': 'infobox'})
                    if infobox:
                        for row in infobox.find_all('tr'):
                            header = row.find('th')
                            if not header:
                                continue
                                
                            header_text = header.get_text().lower().strip()
                            data_cell = row.find('td')
                            
                            if not data_cell:
                                continue
                            
                            # Extract and clean release date
                            if 'release' in header_text:
                                raw_date = data_cell.get_text().strip()
                                # Clean up the date formatting
                                game_info["release_date"] = _clean_release_date(raw_date)
                            
                            # Extract and clean genre
                            elif 'genre' in header_text:
                                raw_genre = data_cell.get_text().strip()
                                game_info["genre"] = _clean_genre(raw_genre)
                            
                            # Extract and clean platforms
                            elif 'platform' in header_text:
                                raw_platforms = data_cell.get_text().strip()
                                game_info["platforms"] = _clean_platforms(raw_platforms)
                    
                    if content_parts:
                        # Description: Short summary (first 2 sentences)
                        first_para = content_parts[0]
                        sentences = first_para.split('. ')
                        if len(sentences) >= 2:
                            game_info["description"] = '. '.join(sentences[:2]) + '.'
                        else:
                            game_info["description"] = sentences[0] + '.' if not sentences[0].endswith('.') else sentences[0]
                        
                        # Sources content: Full paragraph for detailed reference
                        game_info["sources"].append({
                            "url": wiki_url,
                            "content": first_para[:500] + "..." if len(first_para) > 500 else first_para
                        })
                        
            except Exception as e:
                pass  # Continue to fallback
            
            # If Wikipedia fails or provides insufficient data, try alternative approach
            if not game_info["description"]:
                # Create a structured fallback with what we know
                game_info["description"] = f"{game_name} is a video game. Detailed information is not available due to web scraping limitations."
                
                # Add some common gaming platforms as fallback
                if not game_info["platforms"]:
                    game_info["platforms"] = ["PC", "Steam"]
                
                game_info["sources"].append({
                    "url": "fallback",
                    "content": f"Basic information for {game_name}. For detailed reviews and information, check gaming websites like IGN, GameSpot, or Steam store page."
                })
            
            return game_info
            
    except Exception as e:
        return {
            "error": str(e), 
            "game_name": game_name,
            "description": f"Search failed for {game_name}"
        }


def _clean_release_date(raw_date: str) -> str:
    """Clean and format release date from Wikipedia."""
    if not raw_date:
        return ""
    
    # Remove common Wikipedia formatting artifacts
    cleaned = re.sub(r'\[.*?\]', '', raw_date)  # Remove citations
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Normalize whitespace
    
    # Try to extract main release date (often the first one mentioned)
    # Look for patterns like "August 3, 2023" or "3 August 2023"
    date_patterns = [
        r'(\d{1,2}\s+\w+\s+\d{4})',  # "3 August 2023"
        r'(\w+\s+\d{1,2},?\s+\d{4})',  # "August 3, 2023"
        r'(\d{4})',  # Just year as fallback
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, cleaned)
        if match:
            return match.group(1)
    
    # If no pattern matches, return first 50 characters
    return cleaned[:50] if len(cleaned) > 50 else cleaned


def _clean_genre(raw_genre: str) -> str:
    """Clean and format genre from Wikipedia."""
    if not raw_genre:
        return ""
    
    # Remove citations and extra formatting
    cleaned = re.sub(r'\[.*?\]', '', raw_genre)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Take first genre if multiple are listed
    if ',' in cleaned:
        return cleaned.split(',')[0].strip()
    
    return cleaned[:50] if len(cleaned) > 50 else cleaned


def _clean_platforms(raw_platforms: str) -> List[str]:
    """Clean and format platforms from Wikipedia."""
    if not raw_platforms:
        return []
    
    # Remove citations and extra formatting
    cleaned = re.sub(r'\[.*?\]', '', raw_platforms)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Split platforms that are often concatenated together
    # Common patterns: "WindowsPlayStation 5macOS" -> ["Windows", "PlayStation 5", "macOS"]
    platform_patterns = [
        r'(Windows)',
        r'(PlayStation\s*\d*)',
        r'(Xbox\s*(?:Series\s*[XS]|One)?)', 
        r'(macOS)',
        r'(iOS)',
        r'(Android)',
        r'(Linux)',
        r'(Nintendo\s*Switch)',
        r'(Steam)',
        r'(PC)',
    ]
    
    found_platforms = []
    remaining_text = cleaned
    
    # Extract known platforms first
    for pattern in platform_patterns:
        matches = re.findall(pattern, remaining_text, re.IGNORECASE)
        for match in matches:
            platform_name = match.strip()
            if platform_name and platform_name not in found_platforms:
                found_platforms.append(platform_name)
        # Remove found platforms from remaining text
        remaining_text = re.sub(pattern, '', remaining_text, flags=re.IGNORECASE)
    
    # If we found platforms with pattern matching, use those
    if found_platforms:
        return found_platforms[:6]
    
    # Fallback: split by common separators
    separators = [',', ';', '\n', '  ']  # Double space often separates platforms
    platforms = [cleaned]
    
    for sep in separators:
        new_platforms = []
        for platform in platforms:
            new_platforms.extend(platform.split(sep))
        platforms = new_platforms
    
    # Clean each platform name
    cleaned_platforms = []
    for platform in platforms:
        platform = platform.strip()
        if platform and len(platform) > 2:  # Skip very short entries
            # Clean common platform names
            platform = re.sub(r'^\W+', '', platform)  # Remove leading symbols
            platform = re.sub(r'\W+$', '', platform)  # Remove trailing symbols
            if platform:
                cleaned_platforms.append(platform)
    
    return cleaned_platforms[:6]  # Limit to 6 platforms


def _clean_wikipedia_text(text: str) -> str:
    """Clean Wikipedia paragraph text for better readability."""
    if not text:
        return ""
    
    # Remove citations and references [1], [citation needed], etc.
    cleaned = re.sub(r'\[.*?\]', '', text)
    
    # Remove pronunciation guides in parentheses that start with /
    cleaned = re.sub(r'\(/[^)]*\)', '', cleaned)
    
    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Remove common Wikipedia artifacts
    artifacts_to_remove = [
        'Listen to this article',
        'This article is about',
        'For other uses, see',
        'Not to be confused with',
    ]
    
    for artifact in artifacts_to_remove:
        if artifact in cleaned:
            # Remove the entire sentence containing the artifact
            sentences = cleaned.split('.')
            cleaned_sentences = [s for s in sentences if artifact not in s]
            cleaned = '. '.join(cleaned_sentences)
    
    # Ensure it ends properly
    if cleaned and not cleaned.endswith('.'):
        # Find the last complete sentence
        last_period = cleaned.rfind('.')
        if last_period > len(cleaned) * 0.7:  # If the last period is in the latter part
            cleaned = cleaned[:last_period + 1]
        else:
            cleaned += '.'
    
    return cleaned.strip()


@tool
def get_game_summary(game_name: str) -> Dict[str, Any]:
    """Get a concise game summary optimized for content creation."""
    try:
        # Create a structured summary based on common game information
        game_data = {
            "game_name": game_name,
            "summary": "",
            "key_features": [],
            "target_audience": "",
            "content_ideas": []
        }
        
        # Generate content based on game name patterns and common knowledge
        game_lower = game_name.lower()
        
        # Known popular games database (small subset)
        game_database = {
            "baldur's gate 3": {
                "summary": "Baldur's Gate 3 is a critically acclaimed RPG based on Dungeons & Dragons 5th Edition, featuring turn-based combat, deep character customization, and branching storylines with meaningful choices.",
                "key_features": ["Turn-based combat", "D&D 5e rules", "Character customization", "Branching narratives", "Co-op multiplayer"],
                "target_audience": "RPG enthusiasts, D&D fans, story-driven gamers"
            },
            "cyberpunk 2077": {
                "summary": "Cyberpunk 2077 is an open-world action RPG set in a dystopian future Night City, featuring first-person gameplay, character customization, and a branching narrative.",
                "key_features": ["Open world", "Character customization", "Futuristic setting", "Action RPG elements", "Story choices"],
                "target_audience": "Action RPG fans, sci-fi enthusiasts, open-world gamers"
            },
            "elden ring": {
                "summary": "Elden Ring is a challenging action RPG from FromSoftware, combining Dark Souls gameplay with an open-world setting created in collaboration with George R.R. Martin.",
                "key_features": ["Challenging combat", "Open world exploration", "Rich lore", "Character builds", "Boss battles"],
                "target_audience": "Souls-like fans, challenge seekers, fantasy RPG players"
            }
        }
        
        # Check if we have specific data for this game
        if game_lower in game_database:
            game_info = game_database[game_lower]
            game_data.update(game_info)
        else:
            # Generate based on patterns
            if any(word in game_lower for word in ["rpg", "fantasy", "magic", "dragon", "quest", "dungeon"]):
                game_data["summary"] = f"{game_name} is a role-playing game featuring fantasy elements, character progression, and immersive storytelling."
                game_data["key_features"] = ["Character customization", "Story-driven gameplay", "Fantasy setting", "Character progression"]
                game_data["target_audience"] = "RPG enthusiasts and story-driven gamers"
                
            elif any(word in game_lower for word in ["shooter", "fps", "call of duty", "battlefield", "valorant"]):
                game_data["summary"] = f"{game_name} is a first-person shooter with competitive multiplayer and action-packed gameplay."
                game_data["key_features"] = ["Multiplayer combat", "Weapon customization", "Competitive gameplay", "Team-based action"]
                game_data["target_audience"] = "FPS and competitive gaming community"
                
            elif any(word in game_lower for word in ["craft", "build", "sim", "city", "minecraft"]):
                game_data["summary"] = f"{game_name} is a simulation/building game focusing on creativity and strategic planning."
                game_data["key_features"] = ["Creative building", "Resource management", "Open-ended gameplay", "Sandbox elements"]
                game_data["target_audience"] = "Creative gamers and simulation fans"
                
            else:
                game_data["summary"] = f"{game_name} is a popular video game that has gained attention in the gaming community for its unique gameplay and engaging features."
                game_data["key_features"] = ["Engaging gameplay", "Unique mechanics", "Community following"]
                game_data["target_audience"] = "General gaming audience"
        
        # Generate content ideas based on the game
        game_data["content_ideas"] = [
            f"Complete beginner's guide to {game_name}",
            f"Top 10 tips and tricks for {game_name}",
            f"{game_name} honest review and first impressions",
            f"Best builds/strategies for {game_name}",
            f"Is {game_name} worth buying in 2024?",
            f"{game_name} vs similar games comparison"
        ]
        
        return game_data
        
    except Exception as e:
        return {
            "error": str(e),
            "game_name": game_name,
            "summary": f"Unable to generate summary for {game_name}"
        }