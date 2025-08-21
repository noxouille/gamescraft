# GamesCraft AI - Multi-Agent System for YouTube Gaming Content Creation

GamesCraft AI is a powerful multi-agent system designed to help YouTube gaming content creators streamline their content creation process. It uses LangGraph and OpenAI to provide intelligent assistance for creating video scripts, researching gaming topics, and generating thumbnail concepts.

## Features

- **Multi-Language Support**: Works in English and French
- **Intent Recognition**: Automatically understands whether you want event summaries or game content
- **Three Specialized Agents**:
  - **Research Agent**: Gathers comprehensive information about games and gaming events
  - **Script Writer Agent**: Creates production-ready video scripts with timestamps
  - **YouTube Coach Agent**: Generates viral thumbnail concepts for maximum engagement

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for Python package and environment management.

### Prerequisites

Install uv:
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Getting Started

1. Clone the repository and navigate to the project directory

2. Copy the environment file and add your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. Create virtual environment:
```bash
uv venv
```

4. Activate the environment:
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

5. Install dependencies:
```bash
# Install all dependencies
uv pip install -e .
```

6. Run the application:
```bash
python main.py
```

## Usage Examples

### Event Summary
```
English: "Make a 15-min summary of Xbox Showcase [URL]"
French: "Fais un résumé de 15 minutes du Nintendo Direct [URL]"
```

### Game Content
```
English: "Create a 10-minute review video about Baldur's Gate 3"
French: "Crée une vidéo de 20 minutes sur Hogwarts Legacy"
```

## Project Structure

```
gamescraft/
├── agents/              # Agent implementations
│   ├── research_agent.py
│   ├── script_writer_agent.py
│   └── youtube_coach_agent.py
├── tools/               # Tool definitions for agents
├── workflows/           # LangGraph workflow orchestration
├── config/              # Configuration management
├── main.py              # Main application entry point
└── pyproject.toml       # Project configuration and dependencies
```

## How It Works

1. **Query Processing**: The system detects the language and intent of your request
2. **Research Phase**: The Research Agent gathers information from the web and YouTube
3. **Script Creation**: The Script Writer Agent creates a complete video script with timestamps
4. **Thumbnail Generation**: The YouTube Coach Agent generates 3 viral thumbnail concepts
5. **Output**: All results are displayed and can be saved to JSON files

## Requirements

- Python 3.11+
- OpenAI API key
- Internet connection for web scraping and YouTube data