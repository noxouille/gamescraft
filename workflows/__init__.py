from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from agents import AgentState, ResearchAgent, ScriptWriterAgent, YouTubeCoachAgent
from llm_client.config import get_config


class GamesCraftWorkflow:
    def __init__(self):
        self.config = get_config()
        
        self.research_agent = ResearchAgent()
        self.script_writer = ScriptWriterAgent()
        self.youtube_coach = YouTubeCoachAgent()
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        workflow.add_node("intent_detection", self._detect_intent)
        workflow.add_node("research", self._research_node)
        workflow.add_node("script_writing", self._script_writing_node)
        workflow.add_node("thumbnail_generation", self._thumbnail_node)
        
        workflow.set_entry_point("intent_detection")
        
        workflow.add_edge("intent_detection", "research")
        workflow.add_edge("research", "script_writing")
        workflow.add_edge("script_writing", "thumbnail_generation")
        workflow.add_edge("thumbnail_generation", END)
        
        return workflow.compile()
    
    async def _detect_intent(self, state: AgentState) -> AgentState:
        query_lower = state.query.lower()
        
        state.language = self._detect_language(query_lower)
        
        if any(keyword in query_lower for keyword in ["summary", "résumé", "showcase", "direct", "event"]):
            state.intent = "event_summary"
        elif any(keyword in query_lower for keyword in ["review", "critique", "video", "vidéo", "about", "sur"]):
            state.intent = "game_content"
        else:
            state.intent = "general"
        
        state.messages.append(
            HumanMessage(content=f"Query: {state.query} | Intent: {state.intent} | Language: {state.language}")
        )
        state.current_agent = "Research"
        
        return state
    
    def _detect_language(self, text: str) -> str:
        french_keywords = ["fais", "crée", "vidéo", "critique", "résumé", "sur", "de", "minutes"]
        french_count = sum(1 for keyword in french_keywords if keyword in text)
        return "fr" if french_count >= 2 else "en"
    
    async def _research_node(self, state: AgentState) -> AgentState:
        return await self.research_agent.process(state)
    
    async def _script_writing_node(self, state: AgentState) -> AgentState:
        return await self.script_writer.process(state)
    
    async def _thumbnail_node(self, state: AgentState) -> AgentState:
        return await self.youtube_coach.process(state)
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        initial_state = AgentState(
            query=query,
            messages=[],
            current_agent="intent_detection"
        )
        
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            
            return {
                "success": True,
                "query": query,
                "language": final_state.language,
                "intent": final_state.intent,
                "research": final_state.research_data,
                "script": final_state.script,
                "thumbnails": final_state.thumbnails,
                "messages": [msg.content for msg in final_state.messages],
                "error": final_state.error
            }
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": str(e)
            }