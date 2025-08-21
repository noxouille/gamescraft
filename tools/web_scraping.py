"""
Web scraping tools for GamesCraft AI system.
Handles general web content extraction and processing.
"""

from typing import Dict
from bs4 import BeautifulSoup
import httpx
from langchain_core.tools import tool


@tool
def scrape_web_content(url: str) -> Dict[str, str]:
    """Scrape content from a web page."""
    try:
        with httpx.Client() as client:
            response = client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            title = soup.find("title")
            title_text = title.string if title else ""
            
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc.get("content", "") if meta_desc else ""
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)
            
            return {
                "title": title_text,
                "description": description,
                "content": text[:5000],
                "url": url
            }
    except Exception as e:
        return {"error": str(e)}