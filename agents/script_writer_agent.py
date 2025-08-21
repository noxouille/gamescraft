from typing import Dict, Any
from langchain_core.messages import AIMessage
from .base import BaseAgent, AgentState


class ScriptWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__("Script Writer Agent")
    
    async def process(self, state: AgentState) -> AgentState:
        language_map = {"en": "English", "fr": "French"}
        language = language_map.get(state.language, "English")
        
        duration_match = self._extract_duration(state.query)
        duration = duration_match if duration_match else 10
        
        research_summary = state.research_data.get("summary", "No research data available")
        
        system_prompt = f"""You are a professional YouTube gaming content script writer.
Create engaging, well-structured video scripts with proper timestamps.

Script Requirements:
- Include timestamps for each section
- Hook viewers in the first 15 seconds
- Maintain engaging pacing throughout
- Include calls-to-action (like, subscribe, comment)
- End with a strong conclusion

Adapt your tone based on content type:
- Reviews: Analytical and balanced
- Event summaries: Exciting and informative
- Game previews: Enthusiastic and speculative

Always write in {language} language.
Target duration: {duration} minutes."""

        script_prompt = f"""Based on this research data, create a video script:

Research Summary: {research_summary}
Query: {state.query}
Intent: {state.intent}

Create a complete, production-ready script with timestamps."""
        
        try:
            response = self.llm_client.chat(
                message=script_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            state.script = response
            state.messages.append(AIMessage(content=f"Script created for {duration}-minute video"))
            state.current_agent = "YouTubeCoach"
            
        except Exception as e:
            state.error = f"Script Writer Agent error: {str(e)}"
            state.messages.append(AIMessage(content=f"Error during script writing: {str(e)}"))
        
        return state
    
    def _extract_duration(self, query: str) -> int:
        import re
        duration_pattern = r"(\d+)[\s-]?min"
        match = re.search(duration_pattern, query.lower())
        if match:
            return int(match.group(1))
        return 10