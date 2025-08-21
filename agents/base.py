"""
Base agent classes and interfaces for the GamesCraft AI system.
Provides the foundation for all specialized agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from llm_client.client import LLMClient
from llm_client.config import get_config


class AgentState(BaseModel):
    """
    Shared state object that flows between agents in the workflow.
    Contains all necessary information for the multi-agent pipeline.
    """
    
    # Core query information
    query: str = ""
    language: str = "en"
    intent: str = ""
    
    # Agent outputs
    research_data: Dict[str, Any] = Field(default_factory=dict)
    script: str = ""
    thumbnails: List[str] = Field(default_factory=list)
    
    # Workflow control
    messages: List[BaseMessage] = Field(default_factory=list)
    current_agent: str = ""
    error: Optional[str] = None
    
    # Performance tracking
    processing_time: Dict[str, float] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration for the state model."""
        arbitrary_types_allowed = True


class BaseAgent(ABC):
    """
    Abstract base class for all GamesCraft AI agents.
    Provides common functionality and enforces the agent interface.
    """
    
    def __init__(self, name: str, *, llm_client: Optional[LLMClient] = None):
        """
        Initialize the base agent.
        
        Args:
            name: Human-readable name for the agent
            llm_client: Optional pre-configured LLM client (for testing/injection)
        """
        self.name = name
        self.llm_client = llm_client or LLMClient(get_config())
        self._setup_complete = False
        self._setup()
    
    def _setup(self) -> None:
        """
        Optional setup method for agent-specific initialization.
        Called automatically during __init__.
        """
        self._setup_complete = True
    
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """
        Process the agent state and return the updated state.
        This is the main entry point for agent execution.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state with this agent's contributions
        """
        pass
    
    def _add_message(self, state: AgentState, content: str, message_type: str = "ai") -> None:
        """
        Add a message to the state's message history.
        
        Args:
            state: Agent state to modify
            content: Message content
            message_type: Type of message ("ai", "human", "system")
        """
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
        
        message_classes = {
            "ai": AIMessage,
            "human": HumanMessage,
            "system": SystemMessage
        }
        
        message_class = message_classes.get(message_type, AIMessage)
        state.messages.append(message_class(content=content))
    
    def _set_error(self, state: AgentState, error: str) -> AgentState:
        """
        Set an error on the state and add an error message.
        
        Args:
            state: Agent state to modify
            error: Error description
            
        Returns:
            Modified state with error information
        """
        state.error = f"{self.name} error: {error}"
        self._add_message(state, f"Error in {self.name}: {error}")
        return state
    
    def _record_processing_time(self, state: AgentState, duration: float) -> None:
        """
        Record processing time for this agent.
        
        Args:
            state: Agent state to modify
            duration: Processing time in seconds
        """
        state.processing_time[self.name] = duration
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"