import os
import asyncio
from llm_client.client import LLMClient
from llm_client.config import LLMConfig


def basic_example():
    """Basic usage with automatic configuration from environment variables."""
    client = LLMClient()
    question = "What is the capital of France?"
    
    try:
        response = client.chat(
            message=question,
            temperature=0.5
        )
        print(f"Question: {question}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")


def advanced_example():
    """Advanced usage with custom configuration and message history."""
    config = LLMConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY_DEV"),
        together_api_key=os.getenv("TOGETHER_API_KEY_DEV"),
        openai_model="gpt-4",
        together_model="meta-llama/Llama-3-70b-chat-hf"
    )
    
    client = LLMClient(config=config)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about programming."}
    ]
    
    try:
        response = client.complete(
            messages=messages,
            temperature=0.8,
            max_tokens=100
        )
        
        print(f"Provider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"Response: {response.content}")
        
        if response.usage:
            print(f"Tokens used: {response.usage}")
    except Exception as e:
        print(f"Error: {e}")


def fallback_example():
    """Example demonstrating fallback behavior."""
    config = LLMConfig(
        openai_api_key=None,  # Simulate OpenAI not being available
        together_api_key=os.getenv("TOGETHER_API_KEY_DEV")
    )
    
    client = LLMClient(config=config)
    
    messages = [
        {"role": "user", "content": "Tell me a joke about Python."}
    ]
    
    try:
        response = client.complete(
            messages=messages,
            temperature=0.9
        )
        print(f"Response from {response.provider}: {response.content}")
    except Exception as e:
        print(f"Error: {e}")


def streaming_example():
    """Example with streaming (real-time token output)."""
    client = LLMClient()
    
    messages = [
        {"role": "user", "content": "Write a short story about a robot learning to paint."}
    ]
    
    print("Streaming response:")
    print("-" * 40)
    
    try:
        # The streaming happens automatically - tokens are printed as they arrive
        response = client.complete(
            messages=messages,
            temperature=0.7,
            max_tokens=150,
            stream=True
        )
        
        print("-" * 40)
        print(f"\nProvider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"Total length: {len(response.content)} characters")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("Basic Example")
    print("=" * 50)
    basic_example()
    
    print("\n" + "=" * 50)
    print("Advanced Example")
    print("=" * 50)
    advanced_example()
    
    print("\n" + "=" * 50)
    print("Fallback Example")
    print("=" * 50)
    fallback_example()
    
    print("\n" + "=" * 50)
    print("Streaming Example")
    print("=" * 50)
    streaming_example()