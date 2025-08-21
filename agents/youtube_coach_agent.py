from typing import List
from langchain_core.messages import AIMessage
from .base import BaseAgent, AgentState


class YouTubeCoachAgent(BaseAgent):
    def __init__(self):
        super().__init__("YouTube Coach Agent")
    
    async def process(self, state: AgentState) -> AgentState:
        language_map = {"en": "English", "fr": "French"}
        language = language_map.get(state.language, "English")
        
        script_summary = state.script[:500] if state.script else "No script available"
        
        system_prompt = f"""You are a YouTube growth expert specializing in gaming content.
Your task is to create viral thumbnail concepts that maximize click-through rates.

Thumbnail Design Principles:
- High contrast and vibrant colors
- Clear, readable text (if any)
- Emotional faces or reactions
- Curiosity-inducing elements
- Gaming-specific visual elements

Consider current YouTube trends and what works for gaming channels.
Each prompt should be detailed enough for AI image generation.

Always provide descriptions in {language} language."""

        thumbnail_prompt = f"""Based on this video content, create 3 viral thumbnail prompts:

Video Script Summary: {script_summary}
Query: {state.query}
Intent: {state.intent}

Generate 3 different thumbnail concepts optimized for clicks.
Each should be a detailed prompt for image generation.

Format your response as:
1. [Thumbnail description 1]
2. [Thumbnail description 2]  
3. [Thumbnail description 3]"""
        
        try:
            response = self.llm_client.chat(
                message=thumbnail_prompt,
                system_prompt=system_prompt,
                temperature=0.8
            )
            
            thumbnail_list = self._parse_thumbnails(response)
            
            state.thumbnails = thumbnail_list
            state.messages.append(AIMessage(content=f"Generated {len(thumbnail_list)} thumbnail concepts"))
            state.current_agent = "completed"
            
        except Exception as e:
            state.error = f"YouTube Coach Agent error: {str(e)}"
            state.messages.append(AIMessage(content=f"Error during thumbnail generation: {str(e)}"))
        
        return state
    
    def _parse_thumbnails(self, text: str) -> List[str]:
        lines = text.strip().split("\n")
        thumbnails = []
        current_thumbnail = []
        
        for line in lines:
            if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith("-")):
                if current_thumbnail:
                    thumbnails.append(" ".join(current_thumbnail))
                    current_thumbnail = []
                current_thumbnail.append(line.strip())
            elif line.strip() and current_thumbnail:
                current_thumbnail.append(line.strip())
        
        if current_thumbnail:
            thumbnails.append(" ".join(current_thumbnail))
        
        return thumbnails[:3]