from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from .base import BaseAgent, AgentState
from tools import get_youtube_transcript, scrape_web_content, search_youtube_videos, search_game_info


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("Research Agent")
        self.tools = {
            "get_youtube_transcript": get_youtube_transcript,
            "scrape_web_content": scrape_web_content, 
            "search_youtube_videos": search_youtube_videos,
            "search_game_info": search_game_info
        }
    
    async def process(self, state: AgentState) -> AgentState:
        language_map = {"en": "English", "fr": "French"}
        language = language_map.get(state.language, "English")
        
        system_prompt = f"""You are a gaming research specialist. Your task is to gather comprehensive information about games or gaming events.

For EVENT summaries (Xbox Showcase, Nintendo Direct, etc.):
- Extract key announcements and game reveals
- Note important dates and details
- Gather trailer links when available

For GAME content (reviews, previews):
- Find official trailers on YouTube
- Gather gameplay information
- Research release dates, platforms, genre
- Find review scores if available

Always respond in {language} language.
Organize your research in a clear, structured format.

You have access to these tools: {', '.join(self.tools.keys())}"""

        research_prompt = f"""Research the following request: {state.query}

Intent: {state.intent}
Language: {language}

Please provide a comprehensive research summary including:
1. Main content/event details
2. YouTube video links (if applicable)
3. Key facts and dates
4. Any additional relevant information

Based on the query, suggest what tools I should use and what specific searches to perform."""
        
        try:
            # Get research plan from LLM
            response = self.llm_client.chat(
                message=research_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            # For now, create a basic research summary
            # In a more advanced implementation, you'd parse the response
            # and actually execute the suggested tool calls
            research_data = {
                "summary": response,
                "sources": [],
                "videos": [],
                "key_facts": []
            }
            
            state.research_data = research_data
            state.messages.append(AIMessage(content=f"Research completed: {response[:500]}..."))
            state.current_agent = "ScriptWriter"
            
        except Exception as e:
            state.error = f"Research Agent error: {str(e)}"
            state.messages.append(AIMessage(content=f"Error during research: {str(e)}"))
        
        return state