"""
Integration test for QueryAnalyzerAgent and ResearchAgent
Tests the flow of data from query analysis to research.
"""

import asyncio
import json
from typing import Optional
from agents import AgentState, QueryAnalyzerAgent, ResearchAgent


async def test_integration(query: str) -> None:
    """Test the integration between QueryAnalyzer and Research agents."""
    print(f"\n{'='*70}")
    print(f"🎮 QUERY: {query}")
    print(f"{'='*70}")
    
    # Initialize agents
    query_analyzer = QueryAnalyzerAgent()
    research_agent = ResearchAgent()
    
    # Create initial state
    state = AgentState(query=query)
    
    # Step 1: Query Analysis
    print("\n" + "─"*70)
    print("📊 STEP 1: QUERY ANALYSIS")
    print("─"*70)
    
    state = await query_analyzer.process(state)
    
    if not state.is_relevant:
        print(f"❌ Query rejected: {state.error}")
        return
    
    print(f"✅ Query validated as relevant")
    print(f"  • Language: {state.language}")
    print(f"  • Intent: {state.intent}")
    print(f"  • Event: {state.event_name or 'None'}")
    print(f"  • Games: {', '.join(state.game_names) if state.game_names else 'None'}")
    
    if state.query_context:
        print(f"  • Context:")
        for key, value in state.query_context.items():
            if value:
                print(f"    - {key}: {value}")
    
    # Step 2: Research
    print("\n" + "─"*70)
    print("🔍 STEP 2: RESEARCH")
    print("─"*70)
    print("Starting research based on extracted information...")
    
    state = await research_agent.process(state)
    
    # Display research results
    if state.research_data:
        print("\n✅ Research completed successfully!")
        
        # YouTube Videos
        if "youtube_videos" in state.research_data:
            videos = state.research_data["youtube_videos"]
            print(f"\n📹 Found {len(videos)} YouTube videos:")
            for i, video in enumerate(videos[:3], 1):  # Show first 3
                print(f"  {i}. {video.get('title', 'Unknown title')}")
                if 'url' in video:
                    print(f"     URL: {video['url']}")
        
        # Game Information
        if "game_info" in state.research_data:
            game_info = state.research_data["game_info"]
            print(f"\n🎮 Game Information:")
            for game, info in game_info.items():
                print(f"  • {game}:")
                if isinstance(info, dict):
                    if 'description' in info:
                        desc = info['description'][:150] + "..." if len(info.get('description', '')) > 150 else info.get('description', '')
                        print(f"    Description: {desc}")
                    if 'release_date' in info:
                        print(f"    Release Date: {info['release_date']}")
                    if 'platforms' in info:
                        print(f"    Platforms: {info['platforms']}")
        
        # Web Content
        if "web_content" in state.research_data:
            web_content = state.research_data["web_content"]
            print(f"\n🌐 Web Research:")
            for url, content in list(web_content.items())[:2]:  # Show first 2
                if isinstance(content, dict) and 'title' in content:
                    print(f"  • {content['title']}")
                    print(f"    URL: {url}")
    else:
        print("⚠️  No research data collected")
    
    # Display agent messages
    print("\n" + "─"*70)
    print("💬 AGENT MESSAGES")
    print("─"*70)
    for msg in state.messages:
        print(f"  [{msg.__class__.__name__}] {msg.content[:200]}...")
    
    # Display any errors
    if state.error:
        print(f"\n⚠️  Error occurred: {state.error}")


async def test_multiple_queries():
    """Test multiple queries to see different scenarios."""
    test_queries = [
        # English game review
        "Create a 15-minute review video about Baldur's Gate 3 focusing on combat and story",
        
        # French event summary  
        "Fais un résumé de 10 minutes du Xbox Showcase avec Starfield et Forza",
        
        # Multiple games comparison
        "Make a video comparing Dark Souls 3, Elden Ring, and Sekiro",
        
        # Gaming event coverage
        "Create a summary of Nintendo Direct focusing on Zelda and Mario games",
        
        # Non-relevant query (should be rejected)
        "How to cook pasta carbonara"
    ]
    
    print("\n" + "="*70)
    print("🎮 GAMESCRAFT AI - AGENT INTEGRATION TEST")
    print("Testing QueryAnalyzer → Research Agent Pipeline")
    print("="*70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*70}")
        print(f"TEST {i}/{len(test_queries)}")
        try:
            await test_integration(query)
        except Exception as e:
            print(f"\n❌ Error in test {i}: {e}")
        
        # Small delay between tests
        if i < len(test_queries):
            print(f"\n⏳ Waiting before next test...")
            await asyncio.sleep(2)
    
    print("\n" + "="*70)
    print("✅ INTEGRATION TEST COMPLETE")
    print("="*70)


async def interactive_test():
    """Interactive mode for custom queries."""
    print("\n" + "="*70)
    print("🎮 GAMESCRAFT AI - INTERACTIVE INTEGRATION TEST")
    print("QueryAnalyzer → Research Agent Pipeline")
    print("="*70)
    print("\nEnter queries to test the full pipeline (type 'quit' to exit)")
    
    while True:
        query = input("\n📝 Enter query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            print("⚠️  Please enter a query")
            continue
        
        try:
            await test_integration(query)
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def main():
    """Main entry point."""
    import sys
    
    # Check for command line argument
    if len(sys.argv) > 1:
        if sys.argv[1] == "--batch":
            await test_multiple_queries()
        else:
            # Single query from command line
            query = " ".join(sys.argv[1:])
            await test_integration(query)
    else:
        # Interactive mode by default
        print("\n🎮 GamesCraft Agent Integration Test")
        print("="*50)
        print("Options:")
        print("1. Interactive mode (custom queries)")
        print("2. Batch test (predefined queries)")
        print("3. Single query test")
        print("-"*50)
        
        choice = input("Select option (1/2/3): ").strip()
        
        if choice == "1":
            await interactive_test()
        elif choice == "2":
            await test_multiple_queries()
        elif choice == "3":
            query = input("Enter query: ").strip()
            if query:
                await test_integration(query)
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")