"""Custom Search Algorithm Package

A semantic search engine that combines web search APIs, crawling, and graph-based ranking.
"""

__version__ = "0.1.0"

from .api.search_api import brave_search
from .core.crawler import crawl_pages
from .core.graph_builder import build_graph
from .core.priority_queue import PriorityQueue

__all__ = [
    "brave_search",
    "crawl_pages", 
    "build_graph",
    "PriorityQueue"
]