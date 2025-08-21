#!/usr/bin/env python3
"""
Unified Test Suite for GamesCraft AI Tools
A modular, intelligent test system that adapts to interactive and automated environments.
"""

import sys
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from tools import (
    get_youtube_transcript,
    scrape_web_content,
    search_youtube_videos,
    search_game_info,
    get_game_summary
)


class TestMode(Enum):
    AUTO = "auto"
    INTERACTIVE = "interactive"
    SYNC = "sync"
    ASYNC = "async"
    COMPREHENSIVE = "comprehensive"


@dataclass
class TestCase:
    """Individual test case configuration."""
    tool: Callable
    tool_name: str
    test_data: List[Dict[str, Any]]
    description: str
    async_capable: bool = False


@dataclass
class TestResult:
    """Test execution result."""
    tool_name: str
    test_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0


class TestRunner:
    """Modular test runner with multiple execution strategies."""
    
    def __init__(self):
        self.test_cases = self._define_test_cases()
        self.mode = self._detect_environment()
    
    def _detect_environment(self) -> TestMode:
        """Auto-detect if running in interactive or automated environment."""
        if not sys.stdin.isatty():
            return TestMode.AUTO
        return TestMode.INTERACTIVE
    
    def _define_test_cases(self) -> List[TestCase]:
        """Define all available test cases."""
        return [
            TestCase(
                tool=get_youtube_transcript,
                tool_name="YouTube Transcript",
                description="Extract transcripts from YouTube videos",
                test_data=[
                    {
                        "name": "Rick Roll (Popular Video)",
                        "params": {"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
                    },
                    {
                        "name": "Gaming Video",
                        "params": {"video_url": "https://www.youtube.com/watch?v=invalid123"}
                    }
                ],
                async_capable=True
            ),
            TestCase(
                tool=scrape_web_content,
                tool_name="Web Scraping",
                description="Scrape content from web pages",
                test_data=[
                    {
                        "name": "Test HTML Page",
                        "params": {"url": "https://httpbin.org/html"}
                    },
                    {
                        "name": "Gaming News Site",
                        "params": {"url": "https://www.ign.com"}
                    },
                    {
                        "name": "Invalid URL",
                        "params": {"url": "https://invalid-url-test.xyz"}
                    }
                ],
                async_capable=True
            ),
            TestCase(
                tool=search_youtube_videos,
                tool_name="YouTube Search",
                description="Search for YouTube videos",
                test_data=[
                    {
                        "name": "Gaming News Query",
                        "params": {"query": "gaming news", "max_results": 3}
                    },
                    {
                        "name": "Game Review Query",
                        "params": {"query": "Trails in the Sky the 1st review", "max_results": 3}
                    },
                    {
                        "name": "Nintendo Direct Query",
                        "params": {"query": "Nintendo Direct 2024", "max_results": 2}
                    }
                ],
                async_capable=False
            ),
            TestCase(
                tool=search_game_info,
                tool_name="Game Information (Wikipedia)",
                description="Extract game information from Wikipedia",
                test_data=[
                    {
                        "name": "Trails in the Sky the 1st",
                        "params": {"game_name": "Trails in the Sky the 1st"}
                    },
                    {
                        "name": "Cyberpunk 2077",
                        "params": {"game_name": "Cyberpunk 2077"}
                    },
                    {
                        "name": "Minecraft",
                        "params": {"game_name": "Minecraft"}
                    }
                ],
                async_capable=False
            ),
            TestCase(
                tool=get_game_summary,
                tool_name="Game Summary (Content-Optimized)",
                description="Generate content-creator-friendly game summaries",
                test_data=[
                    {
                        "name": "Trails in the Sky the 1st Summary",
                        "params": {"game_name": "Trails in the Sky the 1st"}
                    },
                    {
                        "name": "Elden Ring Summary",
                        "params": {"game_name": "Elden Ring"}
                    },
                    {
                        "name": "Unknown Game Summary",
                        "params": {"game_name": "Super Obscure Game 2024"}
                    }
                ],
                async_capable=False
            )
        ]
    
    def print_header(self, title: str, char: str = "=", width: int = 70):
        """Print formatted section header."""
        print(f"\n{char * width}")
        print(f"{title:^{width}}")
        print(f"{char * width}")
    
    def print_subheader(self, title: str, char: str = "-", width: int = 50):
        """Print formatted subsection header."""
        print(f"\n{char * width}")
        print(f"🧪 {title}")
        print(f"{char * width}")
    
    def format_result(self, result: TestResult) -> str:
        """Format test result for display."""
        status = "✅ PASS" if result.success else "❌ FAIL"
        time_str = f"({result.execution_time:.2f}s)" if result.execution_time > 0 else ""
        
        output = f"\n{status} {result.test_name} {time_str}\n"
        
        if result.error:
            output += f"❌ Error: {result.error}\n"
        elif result.success:
            # Format the actual result
            if isinstance(result.result, dict):
                if result.result.get("sources") == [] and result.result.get("description") == "":
                    output += "⚠️  No data retrieved (network restrictions)\n"
                else:
                    output += "✅ Success! Data retrieved:\n"
            
            # Show truncated result
            result_str = json.dumps(result.result, indent=2, ensure_ascii=False)
            if len(result_str) > 600:
                output += result_str[:600] + "\n... (truncated)\n"
            else:
                output += result_str + "\n"
        
        return output
    
    def run_single_test(self, test_case: TestCase, test_data: Dict[str, Any]) -> TestResult:
        """Run a single test case."""
        import time
        
        start_time = time.time()
        try:
            result = test_case.tool.invoke(test_data["params"])
            execution_time = time.time() - start_time
            
            # Determine success
            success = True
            error = None
            
            if isinstance(result, dict) and "error" in result and result["error"] is not None:
                success = False
                error = result["error"]
            elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and "error" in result[0]:
                success = False
                error = result[0]["error"]
            
            return TestResult(
                tool_name=test_case.tool_name,
                test_name=test_data["name"],
                success=success,
                result=result,
                error=error,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                tool_name=test_case.tool_name,
                test_name=test_data["name"],
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time
            )
    
    def run_test_suite(self, mode: TestMode = None, selected_tools: List[str] = None) -> List[TestResult]:
        """Run the complete test suite."""
        if mode is None:
            mode = self.mode
        
        results = []
        test_cases = self.test_cases
        
        # Filter by selected tools if specified
        if selected_tools:
            test_cases = [tc for tc in test_cases if tc.tool_name in selected_tools]
        
        self.print_header("GAMESCRAFT AI TOOLS TEST SUITE")
        print(f"🔧 Mode: {mode.value.upper()}")
        print(f"🎯 Testing {len(test_cases)} tool categories")
        print("⚠️  Some failures are expected (network restrictions, rate limits)")
        
        for test_case in test_cases:
            self.print_subheader(f"{test_case.tool_name} - {test_case.description}")
            
            # Determine how many tests to run based on mode
            test_data_to_run = test_case.test_data
            if mode == TestMode.AUTO:
                test_data_to_run = test_case.test_data[:1]  # Just first test in auto mode
            elif mode == TestMode.COMPREHENSIVE:
                test_data_to_run = test_case.test_data  # All tests
            
            for test_data in test_data_to_run:
                print(f"\n🎮 Testing: {test_data['name']}")
                result = self.run_single_test(test_case, test_data)
                results.append(result)
                print(self.format_result(result))
        
        return results
    
    def display_summary(self, results: List[TestResult]):
        """Display test summary."""
        self.print_header("TEST SUMMARY")
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n🔍 Failed Tests:")
            for result in results:
                if not result.success:
                    print(f"   • {result.tool_name}: {result.test_name}")
        
        print(f"\n💡 Next Steps:")
        print(f"   • Review results above for any critical failures")
        print(f"   • Test the full multi-agent system: uv run python main.py")
        print(f"   • Check network connectivity if many tests failed")
    
    def interactive_menu(self):
        """Display interactive menu for test selection."""
        while True:
            self.print_header("INTERACTIVE TEST MENU")
            print("1. 🚀 Quick Auto Test (1 test per tool)")
            print("2. 📊 Comprehensive Test (all test cases)")
            print("3. 🎯 Select Specific Tools")
            print("4. ⚡ Sync Tests Only")
            print("5. 🔄 Async Tests Only (where available)")
            print("6. ❌ Exit")
            
            try:
                choice = input("\nEnter your choice (1-6): ").strip()
                
                if choice == "1":
                    return self.run_test_suite(TestMode.AUTO)
                elif choice == "2":
                    return self.run_test_suite(TestMode.COMPREHENSIVE)
                elif choice == "3":
                    return self._select_tools_menu()
                elif choice == "4":
                    return self.run_test_suite(TestMode.SYNC)
                elif choice == "5":
                    return self.run_test_suite(TestMode.ASYNC)
                elif choice == "6":
                    print("👋 Goodbye!")
                    return []
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                return []
    
    def _select_tools_menu(self) -> List[TestResult]:
        """Tool selection submenu."""
        self.print_subheader("Select Tools to Test")
        
        tool_names = [tc.tool_name for tc in self.test_cases]
        for i, name in enumerate(tool_names, 1):
            print(f"{i}. {name}")
        
        try:
            selections = input("\nEnter tool numbers (comma-separated, e.g., 1,3,5): ").strip()
            if not selections:
                return []
            
            indices = [int(x.strip()) - 1 for x in selections.split(",")]
            selected_tools = [tool_names[i] for i in indices if 0 <= i < len(tool_names)]
            
            if selected_tools:
                return self.run_test_suite(TestMode.COMPREHENSIVE, selected_tools)
            else:
                print("❌ No valid tools selected.")
                return []
                
        except (ValueError, IndexError):
            print("❌ Invalid selection format.")
            return []
    
    def run(self) -> List[TestResult]:
        """Main entry point - run tests based on environment."""
        # Check for command line arguments to force auto mode
        if len(sys.argv) > 1 and sys.argv[1] == "--auto":
            return self.run_test_suite(TestMode.AUTO)
        elif self.mode == TestMode.INTERACTIVE:
            return self.interactive_menu()
        else:
            # Auto mode - run quick tests
            return self.run_test_suite(TestMode.AUTO)


def main():
    """Main function."""
    # Handle help option
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("GamesCraft AI Tools Test Suite")
        print("Usage:")
        print("  python test_tools_unified.py              # Interactive mode (if TTY)")
        print("  python test_tools_unified.py --auto       # Auto mode (quick tests)")
        print("  python test_tools_unified.py --help       # Show this help")
        print("\nModes:")
        print("  Interactive: Menu-driven testing with multiple options")
        print("  Auto:        Quick automated testing (1 test per tool)")
        return
    
    runner = TestRunner()
    results = runner.run()
    
    if results:
        runner.display_summary(results)


if __name__ == "__main__":
    main()