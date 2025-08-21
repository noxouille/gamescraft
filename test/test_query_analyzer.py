"""
Simple CLI test for QueryAnalyzerAgent
Tests query validation and structured information extraction.
"""

import asyncio
import json
from typing import Optional
from agents import AgentState, QueryAnalyzerAgent


async def test_query(query: str) -> None:
    """Test a single query with the QueryAnalyzerAgent."""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    # Create agent and initial state
    agent = QueryAnalyzerAgent()
    state = AgentState(query=query)
    
    # Process the query
    result_state = await agent.process(state)
    
    # Display results
    print(f"\n📊 Analysis Results:")
    print(f"  ✓ Relevant: {result_state.is_relevant}")
    
    if result_state.is_relevant:
        print(f"  ✓ Language: {result_state.language}")
        print(f"  ✓ Intent: {result_state.intent}")
        
        if result_state.event_name:
            print(f"  ✓ Event: {result_state.event_name}")
        
        if result_state.game_names:
            print(f"  ✓ Games: {', '.join(result_state.game_names)}")
        
        if result_state.query_context:
            print(f"  ✓ Context: {json.dumps(result_state.query_context, indent=4)}")
    else:
        print(f"  ✗ Rejection Reason: {result_state.error}")
    
    # Display messages
    if result_state.messages:
        print(f"\n💬 Agent Message:")
        for msg in result_state.messages:
            print(f"  {msg.content}")


async def interactive_mode() -> None:
    """Run interactive testing mode."""
    print("🎮 QueryAnalyzerAgent Interactive Test")
    print("Enter queries to test (type 'quit' to exit)")
    print("-" * 60)
    
    while True:
        query = input("\n📝 Enter query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            print("⚠️  Please enter a query")
            continue
        
        try:
            await test_query(query)
        except Exception as e:
            print(f"❌ Error: {e}")


async def batch_mode() -> None:
    """Run batch testing with predefined queries."""
    test_queries = [
        # Relevant queries
        "Create a 10-minute review video about Baldur's Gate 3",
        "Make a summary of the Xbox Showcase event",
        "Fais une vidéo critique de 15 minutes sur Hogwarts Legacy",
        "I want to create gameplay tutorial for Elden Ring boss fights",
        "Make a video comparing Starfield and No Man's Sky",
        
        # Non-relevant queries
        "How do I fix my computer?",
        "What's the weather today?",
        "Create a cooking video about pasta",
        "Help me with my math homework",
    ]
    
    print("🎮 QueryAnalyzerAgent Batch Test")
    print(f"Testing {len(test_queries)} queries...")
    print("-" * 60)
    
    for query in test_queries:
        try:
            await test_query(query)
        except Exception as e:
            print(f"❌ Error processing '{query}': {e}")
    
    print(f"\n{'='*60}")
    print("✅ Batch test complete!")


async def main():
    """Main entry point for the test script."""
    print("\n🎮 GamesCraft QueryAnalyzerAgent Test CLI")
    print("=" * 60)
    print("Select testing mode:")
    print("1. Interactive mode (enter your own queries)")
    print("2. Batch mode (test predefined queries)")
    print("3. Single query (pass as argument)")
    print("-" * 60)
    
    import sys
    
    # Check if query passed as command line argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        await test_query(query)
        return
    
    choice = input("Enter choice (1/2): ").strip()
    
    if choice == "1":
        await interactive_mode()
    elif choice == "2":
        await batch_mode()
    else:
        print("❌ Invalid choice. Exiting.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")