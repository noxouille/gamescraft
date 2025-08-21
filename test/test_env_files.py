import os
from llm_client.client import LLMClient
from llm_client.config import get_config

print("Testing Environment Configuration")
print("=" * 50)

# Test Development Environment
print("\n1. Loading Development Environment")
print("-" * 40)
dev_config = get_config("development")
print(f"Environment: development")
print(f"OpenAI Model: {dev_config.openai_model}")
print(f"Together Model: {dev_config.together_model}")
print(f"Timeout: {dev_config.timeout}s")
print(f"Dev API Key present: {'Yes' if dev_config.openai_api_key else 'No'}")

# Test Production Environment
print("\n2. Loading Production Environment")
print("-" * 40)
prod_config = get_config("production")
print(f"Environment: production")
print(f"OpenAI Model: {prod_config.openai_model}")
print(f"Together Model: {prod_config.together_model}")
print(f"Timeout: {prod_config.timeout}s")
print(f"Prod API Key present: {'Yes' if prod_config.openai_api_key else 'No'}")

# Test with ENVIRONMENT variable
print("\n3. Loading based on ENVIRONMENT variable")
print("-" * 40)
os.environ["ENVIRONMENT"] = "production"
auto_config = get_config()
print(f"Auto-selected: {os.environ['ENVIRONMENT']}")
print(f"OpenAI Model: {auto_config.openai_model}")

# Example usage with client
print("\n4. Creating LLM Client with environment")
print("-" * 40)
os.environ["ENVIRONMENT"] = "development"
client = LLMClient()
print("Client initialized successfully!")

print("\nNote: Copy .env.example to .env and add your actual API keys")
print("\nEnvironment switching:")
print("- Set ENVIRONMENT=development for dev keys (default)")
print("- Set ENVIRONMENT=production for prod keys")