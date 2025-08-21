import asyncio
from typing import Dict, Any
from workflows import GamesCraftWorkflow
from utils.logger import logger, setup_file_logging
import json

# Setup file logging
setup_file_logging()


class GamesCraftApp:
    def __init__(self):
        self.workflow = GamesCraftWorkflow()
        logger.info("GamesCraft AI System initialized")
    
    async def process_request(self, query: str) -> Dict[str, Any]:
        logger.info(f"Processing query: {query}")
        
        try:
            result = await self.workflow.process_query(query)
            
            if result["success"]:
                logger.info(f"Successfully processed query in {result['language']} with intent: {result['intent']}")
            else:
                logger.error(f"Failed to process query: {result.get('error')}")
            
            return result
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def display_results(self, results: Dict[str, Any]):
        print("\n" + "="*80)
        print("GAMESCRAFT AI - RESULTS")
        print("="*80)
        
        print(f"\n📝 Query: {results['query']}")
        print(f"🌍 Language: {results.get('language', 'Unknown').upper()}")
        print(f"🎯 Intent: {results.get('intent', 'Unknown')}")
        
        if results.get("research"):
            print("\n📚 RESEARCH SUMMARY:")
            print("-" * 40)
            summary = results["research"].get("summary", "No research data")
            print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        if results.get("script"):
            print("\n🎬 VIDEO SCRIPT:")
            print("-" * 40)
            script = results["script"]
            print(script[:800] + "..." if len(script) > 800 else script)
        
        if results.get("thumbnails"):
            print("\n🎨 THUMBNAIL CONCEPTS:")
            print("-" * 40)
            for i, thumbnail in enumerate(results["thumbnails"], 1):
                print(f"\n{i}. {thumbnail}")
        
        if results.get("error"):
            print("\n❌ ERROR:")
            print("-" * 40)
            print(results["error"])
        
        print("\n" + "="*80)


async def main():
    print("\n" + "="*80)
    print("GAMESCRAFT AI SYSTEM")
    print("Multi-Agent System for YouTube Gaming Content Creation")
    print("="*80)
    
    from llm_client.config import get_config
    config = get_config()
    print(f"\n🔧 Environment: {config.environment.upper()}")
    print(f"🤖 OpenAI Model: {config.openai_model}")
    print(f"⚡ Max Retries: {config.max_retries}")
    print(f"⏱️  Timeout: {config.timeout}s")
    
    app = GamesCraftApp()
    
    example_queries = [
        "Make a 15-min summary of Xbox Showcase",
        "Fais un résumé de 15 minutes du Nintendo Direct",
        "Create a 10-minute review video about Baldur's Gate 3",
        "Crée une vidéo de 20 minutes sur Hogwarts Legacy",
    ]
    
    print("\n📌 Example queries:")
    for i, query in enumerate(example_queries, 1):
        print(f"  {i}. {query}")
    
    while True:
        print("\n" + "-"*80)
        query = input("\n💬 Enter your request (or 'quit' to exit): ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Thank you for using GamesCraft AI!")
            break
        
        if not query:
            print("⚠️  Please enter a valid request.")
            continue
        
        print("\n🔄 Processing your request...")
        results = await app.process_request(query)
        app.display_results(results)
        
        save = input("\n💾 Save results to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"gamescraft_output_{results.get('intent', 'unknown')}_{results.get('language', 'en')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ Results saved to {filename}")


if __name__ == "__main__":
    asyncio.run(main())