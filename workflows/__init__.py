from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from agents import AgentState, QueryAnalyzerAgent, ResearchAgent, ScriptWriterAgent, YouTubeCoachAgent
from llm_client.config import get_config


class GamesCraftWorkflow:
    def __init__(self):
        self.config = get_config()
        
        self.query_analyzer = QueryAnalyzerAgent()
        self.research_agent = ResearchAgent()
        self.script_writer = ScriptWriterAgent()
        self.youtube_coach = YouTubeCoachAgent()
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        workflow.add_node("query_analysis", self._query_analysis_node)
        workflow.add_node("research", self._research_node)
        workflow.add_node("script_writing", self._script_writing_node)
        workflow.add_node("thumbnail_generation", self._thumbnail_node)
        
        workflow.set_entry_point("query_analysis")
        
        # Conditional edge: only proceed if query is relevant
        workflow.add_conditional_edges(
            "query_analysis",
            self._should_continue,
            {
                "continue": "research",
                "end": END
            }
        )
        
        workflow.add_edge("research", "script_writing")
        workflow.add_edge("script_writing", "thumbnail_generation")
        workflow.add_edge("thumbnail_generation", END)
        
        return workflow.compile()
    
    async def _query_analysis_node(self, state: AgentState) -> AgentState:
        """Run the query analyzer agent to validate and extract information."""
        return await self.query_analyzer.process(state)
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine whether to continue processing based on query relevance."""
        if state.is_relevant:
            return "continue"
        else:
            return "end"
    
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
            current_agent="query_analysis"
        )
        
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Check if query was rejected as irrelevant
            if not final_state.is_relevant:
                return {
                    "success": False,
                    "query": query,
                    "is_relevant": False,
                    "error": final_state.error or "Query not relevant for YouTube gaming content creation",
                    "messages": [msg.content for msg in final_state.messages]
                }
            
            return {
                "success": True,
                "query": query,
                "is_relevant": True,
                "language": final_state.language,
                "intent": final_state.intent,
                "event_name": final_state.event_name,
                "game_names": final_state.game_names,
                "query_context": final_state.query_context,
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