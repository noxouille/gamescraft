import logging
from typing import Dict, List, Optional, Union
from .config import LLMConfig, get_config
from .providers.base import LLMResponse
from .providers.openai_provider import OpenAIProvider
from .providers.together_provider import TogetherProvider

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or get_config()
        self.primary_provider = None
        self.fallback_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        if self.config.openai_api_key:
            try:
                self.primary_provider = OpenAIProvider(
                    api_key=self.config.openai_api_key,
                    model=self.config.openai_model,
                    timeout=self.config.timeout
                )
                logger.debug(f"Initialized OpenAI provider with model: {self.config.openai_model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI provider: {e}")
        
        if self.config.together_api_key:
            try:
                self.fallback_provider = TogetherProvider(
                    api_key=self.config.together_api_key,
                    model=self.config.together_model,
                    timeout=self.config.timeout
                )
                logger.debug(f"Initialized Together provider with model: {self.config.together_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Together provider: {e}")
    
    def complete(
        self,
        messages: Union[str, List[Dict[str, str]]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_fallback: bool = True,
        **kwargs
    ) -> LLMResponse:
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        errors = []
        
        if self.primary_provider and self.primary_provider.is_available():
            try:
                logger.debug("Attempting completion with primary provider (OpenAI)")
                response = self.primary_provider.complete(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                logger.debug("Successfully completed with primary provider")
                return response
            except Exception as e:
                error_msg = f"Primary provider failed: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        if use_fallback and self.fallback_provider and self.fallback_provider.is_available():
            try:
                logger.debug("Attempting completion with fallback provider (Together)")
                response = self.fallback_provider.complete(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                logger.debug("Successfully completed with fallback provider")
                return response
            except Exception as e:
                error_msg = f"Fallback provider failed: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        if errors:
            raise RuntimeError(f"All providers failed. Errors: {'; '.join(errors)}")
        else:
            raise RuntimeError("No LLM providers available. Please check your API keys.")
    
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        response = self.complete(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.content