from typing import Dict, Any, List
import asyncio
import json
from langchain_core.messages import HumanMessage, AIMessage
from .base import BaseAgent, AgentState
from tools import get_youtube_transcript, scrape_web_content, search_youtube_videos, search_game_info, get_game_summary


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("Research Agent")
        self.tools = {
            "get_youtube_transcript": get_youtube_transcript,
            "scrape_web_content": scrape_web_content, 
            "search_youtube_videos": search_youtube_videos,
            "search_game_info": search_game_info,
            "get_game_summary": get_game_summary
        }
    
    async def process(self, state: AgentState) -> AgentState:
        """
        Execute research based on the query analysis results.
        Uses tools dynamically based on intent and extracted information.
        """
        state.current_agent = self.name
        
        try:
            research_data = {
                "youtube_videos": [],
                "game_info": {},
                "web_content": {},
                "transcripts": {},
                "summary": ""
            }
            
            # Execute tools based on intent and extracted information
            
            # 1. Search for YouTube videos based on games or events
            if state.game_names:
                for game in state.game_names[:2]:  # Limit to first 2 games
                    try:
                        # Search YouTube for game content
                        search_query = f"{game} {state.intent.replace('_', ' ')}"
                        if state.event_name:
                            search_query = f"{state.event_name} {game}"
                        
                        videos_result = self.tools["search_youtube_videos"].invoke({
                            "query": search_query,
                            "max_results": 3
                        })
                        
                        if videos_result and isinstance(videos_result, list):
                            research_data["youtube_videos"].extend(videos_result)
                    except Exception as e:
                        print(f"Error searching YouTube for {game}: {e}")
            
            elif state.event_name:
                # Search for event videos
                try:
                    videos_result = self.tools["search_youtube_videos"].invoke({
                        "query": f"{state.event_name} gaming showcase",
                        "max_results": 3
                    })
                    
                    if videos_result and isinstance(videos_result, list):
                        research_data["youtube_videos"] = videos_result
                except Exception as e:
                    print(f"Error searching YouTube for event: {e}")
            
            # 2. Get game information for mentioned games
            if state.game_names:
                for game in state.game_names[:2]:  # Limit to first 2 games
                    try:
                        # Get detailed game information
                        game_info = self.tools["search_game_info"].invoke({
                            "game_name": game
                        })
                        
                        if game_info:
                            research_data["game_info"][game] = game_info
                        
                        # Also get game summary for content creation
                        game_summary = self.tools["get_game_summary"].invoke({
                            "game_name": game
                        })
                        
                        if game_summary and "summary" in game_summary:
                            if game not in research_data["game_info"]:
                                research_data["game_info"][game] = {}
                            research_data["game_info"][game]["creator_summary"] = game_summary["summary"]
                    except Exception as e:
                        print(f"Error getting game info for {game}: {e}")
            
            # 3. Web research for games and events
            if state.game_names:
                for game in state.game_names[:1]:  # Limit to first game for web research
                    try:
                        # Search for game reviews or news
                        search_urls = [
                            f"https://www.gamespot.com/search/?q={game.replace(' ', '+')}",
                            f"https://www.ign.com/search?q={game.replace(' ', '+')}",
                        ]
                        
                        for url in search_urls[:1]:  # Just try one URL to avoid overwhelming
                            try:
                                web_result = self.tools["scrape_web_content"].invoke({
                                    "url": url
                                })
                                
                                if web_result and "title" in web_result:
                                    research_data["web_content"][url] = web_result
                                    break  # Stop after first successful scrape
                            except Exception as e:
                                print(f"Error scraping {url}: {e}")
                                continue
                    except Exception as e:
                        print(f"Error in web research for {game}: {e}")
            
            # 4. Get transcripts for top videos (if found)
            if research_data["youtube_videos"]:
                for video in research_data["youtube_videos"][:2]:  # First 2 videos
                    if "url" in video:
                        try:
                            transcript_result = self.tools["get_youtube_transcript"].invoke({
                                "video_url": video["url"]
                            })
                            
                            if transcript_result and "transcript" in transcript_result:
                                research_data["transcripts"][video["url"]] = {
                                    "title": video.get("title", "Unknown"),
                                    "transcript": transcript_result["transcript"][:1000]  # Limit length
                                }
                        except Exception as e:
                            print(f"Error getting transcript: {e}")
            
            # 5. Generate research summary using LLM
            summary_prompt = self._build_summary_prompt(state, research_data)
            response_obj = self.llm_client.complete(summary_prompt)
            research_data["summary"] = response_obj.content
            
            # Update state with research results
            state.research_data = research_data
            
            # Add success message
            self._add_message(
                state,
                f"Research completed successfully!\n"
                f"• Found {len(research_data['youtube_videos'])} YouTube videos\n"
                f"• Gathered info for {len(research_data['game_info'])} games\n"
                f"• Collected {len(research_data['transcripts'])} video transcripts"
            )
            
            state.current_agent = "ScriptWriter"
            return state
            
        except Exception as e:
            return self._set_error(state, f"Failed to complete research: {str(e)}")
    
    def _build_summary_prompt(self, state: AgentState, research_data: Dict) -> str:
        """Build prompt for summarizing research results."""
        language_map = {"en": "English", "fr": "French"}
        language = language_map.get(state.language, "English")
        
        return f"""Based on the following research data, create a comprehensive summary for a YouTube content creator.

Query: {state.query}
Intent: {state.intent}
Language: {language}

Research Data:
- YouTube Videos Found: {len(research_data['youtube_videos'])}
- Games Researched: {', '.join(research_data['game_info'].keys()) if research_data['game_info'] else 'None'}
- Video Transcripts Collected: {len(research_data['transcripts'])}

Key Information:
{json.dumps(research_data['game_info'], indent=2) if research_data['game_info'] else 'No game information'}

Please provide a concise summary highlighting:
1. Main findings relevant to the content creation request
2. Key talking points for the video
3. Important dates, facts, or features to mention
4. Suggested structure for the video content

Respond in {language}."""