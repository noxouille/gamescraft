from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from llm_client.client import LLMClient
from llm_client.config import get_config


class AgentState(BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)
    query: str = ""
    language: str = "en"
    intent: str = ""
    research_data: Dict[str, Any] = Field(default_factory=dict)
    script: str = ""
    thumbnails: List[str] = Field(default_factory=list)
    current_agent: str = ""
    error: Optional[str] = None


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.llm_client = LLMClient(get_config())
    
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        pass
    
    def _detect_language(self, text: str) -> str:
        french_keywords = ["fais", "crée", "vidéo", "critique", "résumé", "sur", "de"]
        text_lower = text.lower()
        french_count = sum(1 for keyword in french_keywords if keyword in text_lower)
        return "fr" if french_count >= 2 else "en"