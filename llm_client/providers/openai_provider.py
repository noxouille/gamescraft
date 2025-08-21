import logging
from typing import Dict, List, Optional
from .base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", timeout: int = 30):
        super().__init__(api_key, model, timeout)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                timeout=self.timeout
            )
        except ImportError:
            logger.error("OpenAI library not installed. Run: pip install openai")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
    
    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        if not self.is_available():
            raise RuntimeError("OpenAI client is not available")
        
        try:
            if stream:
                return self._stream_complete(messages, temperature, max_tokens, **kwargs)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None,
                raw_response=response
            )
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}")
            raise
    
    def _stream_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            collected_content = []
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    collected_content.append(content)
                    print(content, end='', flush=True)
            
            print()  # New line after streaming
            full_content = ''.join(collected_content)
            
            return LLMResponse(
                content=full_content,
                model=self.model,
                provider="openai",
                usage=None,
                raw_response=None
            )
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise
    
    def is_available(self) -> bool:
        return self.client is not None and self.api_key is not None