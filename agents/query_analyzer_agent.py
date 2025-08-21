"""
Query Analyzer Agent for GamesCraft AI.
Validates query relevance and extracts structured information for YouTube gaming content creation.
"""

import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage
from .base import BaseAgent, AgentState


class QueryContext(BaseModel):
    """Additional context extracted from the query."""
    duration: Optional[str] = Field(None, description="Requested video duration")
    focus_areas: List[str] = Field(default_factory=list, description="Specific aspects to cover")
    additional_requirements: Optional[str] = Field(None, description="Any other requirements")


class QueryAnalysis(BaseModel):
    """Structured output from query analysis."""
    is_relevant: bool = Field(description="Whether query is relevant for YouTube gaming content")
    rejection_reason: Optional[str] = Field(None, description="Reason if query is not relevant")
    language: str = Field(default="en", description="Language code (en or fr)")
    intent: str = Field(
        default="general_gaming",
        description="Type of content: event_summary, game_review, game_news, gameplay, general_gaming"
    )
    event_name: Optional[str] = Field(None, description="Gaming event name if applicable")
    game_names: List[str] = Field(default_factory=list, description="List of game names mentioned")
    context: QueryContext = Field(default_factory=QueryContext, description="Additional context")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "is_relevant": True,
                "rejection_reason": None,
                "language": "en",
                "intent": "game_review",
                "event_name": None,
                "game_names": ["Baldur's Gate 3", "Starfield"],
                "context": {
                    "duration": "10 minutes",
                    "focus_areas": ["gameplay", "story"],
                    "additional_requirements": "Include comparison"
                }
            }
        }


class QueryAnalyzerAgent(BaseAgent):
    """
    Analyzes user queries to determine relevance to YouTube gaming content creation
    and extracts structured information for downstream agents.
    """
    
    def __init__(self):
        super().__init__("Query Analyzer Agent")
    
    async def process(self, state: AgentState) -> AgentState:
        """
        Process the query to validate relevance and extract structured information.
        
        Args:
            state: Current agent state with user query
            
        Returns:
            Updated state with analysis results
        """
        state.current_agent = self.name
        
        try:
            analysis_prompt = self._build_analysis_prompt(state.query)
            response_obj = self.llm_client.complete(analysis_prompt)
            response = response_obj.content
            
            # Parse the structured response using Pydantic
            analysis = self._parse_analysis_response(response)
            
            # Update state with analysis results
            state.is_relevant = analysis.is_relevant
            state.language = analysis.language
            state.intent = analysis.intent
            state.event_name = analysis.event_name
            state.game_names = analysis.game_names
            state.query_context = analysis.context.dict()
            
            # Add message about analysis results
            if state.is_relevant:
                self._add_message(
                    state, 
                    f"Query validated as relevant for YouTube gaming content creation.\n"
                    f"Language: {state.language}\n"
                    f"Intent: {state.intent}\n"
                    f"Games: {', '.join(state.game_names) if state.game_names else 'None specified'}\n"
                    f"Event: {state.event_name or 'None specified'}"
                )
            else:
                self._add_message(
                    state,
                    f"Query not relevant for YouTube gaming content creation. "
                    f"Reason: {analysis.rejection_reason or 'Does not match gaming content criteria'}"
                )
                state.error = "Query not relevant for gaming content creation"
            
            return state
            
        except Exception as e:
            return self._set_error(state, f"Failed to analyze query: {str(e)}")
    
    def _build_analysis_prompt(self, query: str) -> str:
        """Build the prompt for query analysis with Pydantic schema."""
        schema = QueryAnalysis.schema()
        return f"""You are analyzing a query for a YouTube gaming content creation system.

Query: "{query}"

Analyze this query and determine:

1. RELEVANCE: Is this query relevant to YouTube gaming content creation?
   - Relevant: Game reviews, gaming event summaries, game critiques, gameplay videos, gaming news, game tutorials
   - NOT relevant: Non-gaming topics, general YouTube questions, technical support, unrelated content

2. LANGUAGE: What language is the query in? (en for English, fr for French)

3. INTENT: If relevant, what type of content is requested?
   - "event_summary": Gaming event coverage (E3, Xbox Showcase, Nintendo Direct, etc.)
   - "game_review": Review or critique of specific games
   - "game_news": Gaming news or updates
   - "gameplay": Gameplay videos or tutorials
   - "general_gaming": Other gaming content

4. EXTRACTION: Extract the following if present:
   - Event name (if discussing a gaming event)
   - Game names (list all games mentioned)
   - Additional context (duration requested, specific aspects to cover, etc.)

Respond with a JSON object that matches this exact schema:
{json.dumps(schema, indent=2)}

Example response:
{json.dumps(QueryAnalysis.Config.json_schema_extra["example"], indent=2)}"""
    
    def _parse_analysis_response(self, response: str) -> QueryAnalysis:
        """
        Parse the LLM response into structured data using Pydantic.
        
        Args:
            response: LLM response string
            
        Returns:
            Parsed QueryAnalysis object with validation
        """
        try:
            # Try to extract JSON from the response
            # Handle cases where LLM might include markdown code blocks
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            # Parse JSON and validate with Pydantic
            data = json.loads(response)
            
            # Handle nested context if it's not a QueryContext object
            if "context" in data and isinstance(data["context"], dict):
                data["context"] = QueryContext(**data["context"])
            
            return QueryAnalysis(**data)
            
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback parsing if JSON fails or validation fails
            response_lower = response.lower()
            
            # Basic relevance check
            is_relevant = any(keyword in response_lower for keyword in [
                "relevant", "gaming", "game", "youtube", "video", "content"
            ]) and "not relevant" not in response_lower
            
            # Basic language detection
            language = "fr" if "french" in response_lower or "fr" in response_lower else "en"
            
            # Basic intent detection
            intent = "general_gaming"
            if "event" in response_lower or "showcase" in response_lower:
                intent = "event_summary"
            elif "review" in response_lower or "critique" in response_lower:
                intent = "game_review"
            
            # Return a validated QueryAnalysis object
            return QueryAnalysis(
                is_relevant=is_relevant,
                language=language,
                intent=intent,
                event_name=None,
                game_names=[],
                context=QueryContext(),
                rejection_reason="Could not determine relevance" if not is_relevant else None
            )