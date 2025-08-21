import logging
import requests
from typing import Dict, List, Optional
from .base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class TogetherProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "meta-llama/Llama-3-8b-chat-hf", timeout: int = 30):
        super().__init__(api_key, model, timeout)
        self.base_url = "https://api.together.xyz/v1"
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        try:
            from together import Together
            self.client = Together(api_key=self.api_key)
        except ImportError:
            logger.warning("Together library not installed. Run: pip install together")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Together client: {e}")
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
            raise RuntimeError("Together client is not available")
        
        if self.client:
            return self._complete_with_sdk(messages, temperature, max_tokens, stream, **kwargs)
        else:
            return self._complete_with_api(messages, temperature, max_tokens, stream, **kwargs)
    
    def _complete_with_sdk(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        try:
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
                provider="together",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None,
                raw_response=response
            )
        except Exception as e:
            logger.error(f"Together SDK completion failed: {e}")
            raise
    
    def _complete_with_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                **kwargs
            }
            
            if max_tokens:
                data["max_tokens"] = max_tokens
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            return LLMResponse(
                content=result["choices"][0]["message"]["content"],
                model=result.get("model", self.model),
                provider="together",
                usage=result.get("usage"),
                raw_response=result
            )
        except Exception as e:
            logger.error(f"Together API completion failed: {e}")
            raise
    
    def is_available(self) -> bool:
        return self.api_key is not None