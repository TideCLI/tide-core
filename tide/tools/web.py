"""
Web search tool for getting up-to-date information
"""
import requests
import json
from urllib.parse import quote_plus
from typing import Optional

from .base import Tool, ToolResult, Parameter, ParameterType
from .registry import register_tool


@register_tool
class WebSearchTool(Tool):
    """Search the web for up-to-date information using DuckDuckGo"""
    
    name = "web_search"
    description = "Search the web for current information"
    category = "web"
    
    parameters = {
        "query": Parameter(
            name="query",
            type=ParameterType.STRING,
            description="Search query",
            required=True
        ),
        "num_results": Parameter(
            name="num_results",
            type=ParameterType.INTEGER,
            description="Number of results (1-10)",
            required=False,
            default=5
        )
    }
    
    def _execute(self, query: str, num_results: int = 5) -> ToolResult:
        try:
            # Use DuckDuckGo HTML version (no API key needed)
            num_results = min(max(num_results, 1), 10)
            
            # Try duckduckgo-search library if available
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=num_results))
                    
                    output_lines = [f"🔍 Web Search Results for: '{query}'\n"]
                    for i, result in enumerate(results, 1):
                        title = result.get('title', 'No title')
                        href = result.get('href', 'No URL')
                        body = result.get('body', 'No description')[:200]
                        
                        output_lines.append(f"\n{i}. {title}")
                        output_lines.append(f"   URL: {href}")
                        output_lines.append(f"   {body}...")
                    
                    return ToolResult.success_result(
                        output='\n'.join(output_lines),
                        results=results,
                        count=len(results)
                    )
            except ImportError:
                # Fallback to simple HTML scraping
                pass
            
            # Fallback: return instructions
            return ToolResult.success_result(
                output=f"To enable web search, install: pip install duckduckgo-search\n\n"
                       f"Search query would be: '{query}'",
                query=query
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Search failed: {str(e)}")


@register_tool
class FetchUrlTool(Tool):
    """Fetch content from a URL"""
    
    name = "fetch_url"
    description = "Fetch and read content from a URL"
    category = "web"
    
    parameters = {
        "url": Parameter(
            name="url",
            type=ParameterType.STRING,
            description="URL to fetch",
            required=True
        ),
        "max_length": Parameter(
            name="max_length",
            type=ParameterType.INTEGER,
            description="Maximum characters to return",
            required=False,
            default=5000
        )
    }
    
    def _execute(self, url: str, max_length: int = 5000) -> ToolResult:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; TideOS/1.0)'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            content = response.text
            
            # Try to extract main content (basic HTML stripping)
            try:
                from html.parser import HTMLParser
                
                class TextExtractor(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.text = []
                        self.skip = ['script', 'style', 'nav', 'footer']
                        self.current_tag = None
                    
                    def handle_starttag(self, tag, attrs):
                        self.current_tag = tag
                    
                    def handle_endtag(self, tag):
                        self.current_tag = None
                    
                    def handle_data(self, data):
                        if self.current_tag not in self.skip:
                            self.text.append(data)
                
                extractor = TextExtractor()
                extractor.feed(content)
                text = ' '.join(extractor.text)
                # Clean up whitespace
                text = ' '.join(text.split())
            except:
                text = content
            
            # Truncate if needed
            if len(text) > max_length:
                text = text[:max_length] + f"\n\n... [truncated, total length: {len(content)}]"
            
            return ToolResult.success_result(
                output=f"📄 Fetched: {url}\n"
                       f"Status: {response.status_code}\n"
                       f"Content-Type: {response.headers.get('content-type', 'unknown')}\n"
                       f"\n{'='*50}\n{text}",
                url=url,
                status_code=response.status_code
            )
            
        except requests.RequestException as e:
            return ToolResult.error_result(f"Failed to fetch URL: {str(e)}")
        except Exception as e:
            return ToolResult.error_result(f"Error: {str(e)}")
