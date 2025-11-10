"""
Model Context Protocol server for AI assistant integration.
Enables AI assistants to become telemetry-aware.
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from ..config import config
from ..storage.sqlite_conversations import ConversationStorage
from ..storage.redis_metrics import RedisMetricsStorage


class BlueplaneMCPServer:
    """
    MCP server providing telemetry-aware tools for AI coding assistants.
    Exposes 5 tool categories: Metrics, Analysis, Search, Optimization, Tracking
    """

    def __init__(self, layer2_url: Optional[str] = None):
        """Initialize MCP server with intelligence components."""
        self.server = Server("blueplane-telemetry")
        self.layer2_url = layer2_url or f"http://{config.server_host}:{config.server_port}"
        self.conversation_storage = ConversationStorage()
        self.metrics_storage = RedisMetricsStorage()
        
        # Setup all tool categories
        self._setup_metrics_tools()
        self._setup_analysis_tools()
        self._setup_search_tools()
        self._setup_optimization_tools()
        self._setup_tracking_tools()

    def _setup_metrics_tools(self):
        """Register metrics tools: get_current_metrics, get_session_metrics."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="get_current_metrics",
                    description="Get current session metrics including acceptance rate, productivity, and error rate",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="get_session_metrics",
                    description="Get historical metrics for a specific session or time period",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session ID"},
                            "period": {"type": "string", "description": "Time period (1h, 24h, 7d)"},
                            "platform": {"type": "string", "description": "Platform filter"},
                        },
                    },
                ),
                Tool(
                    name="get_tool_performance",
                    description="Get tool-specific performance data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tool_name": {"type": "string", "description": "Tool name"},
                            "period": {"type": "string", "description": "Time period"},
                        },
                    },
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            if name == "get_current_metrics":
                return await self._get_current_metrics()
            elif name == "get_session_metrics":
                return await self._get_session_metrics(arguments)
            elif name == "get_tool_performance":
                return await self._get_tool_performance(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    def _setup_analysis_tools(self):
        """Register analysis tools: analyze_acceptance_patterns, get_error_patterns."""
        # Add to list_tools and call_tool handlers
        pass  # Placeholder - will implement

    def _setup_search_tools(self):
        """Register search tools: search_similar_tasks, find_successful_patterns."""
        # Add to list_tools and call_tool handlers
        pass  # Placeholder - will implement

    def _setup_optimization_tools(self):
        """Register optimization tools: optimize_context, suggest_strategy."""
        # Add to list_tools and call_tool handlers
        pass  # Placeholder - will implement

    def _setup_tracking_tools(self):
        """Register tracking tools: track_decision, log_outcome."""
        # Add to list_tools and call_tool handlers
        pass  # Placeholder - will implement

    async def _get_current_metrics(self) -> List[TextContent]:
        """Get current session metrics."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.layer2_url}{config.api_prefix}/metrics",
                    timeout=5.0,
                )
                response.raise_for_status()
                data = response.json()
                
                # Format metrics for AI assistant
                metrics_text = f"""Current Telemetry Metrics:

Realtime:
- Active Sessions: {data.get('realtime', {}).get('active_sessions', 'N/A')}
- Events/Second: {data.get('realtime', {}).get('events_per_second', 'N/A')}

Session:
- Acceptance Rate: {data.get('session', {}).get('acceptance_rate', 'N/A')}
- Productivity Score: {data.get('session', {}).get('productivity_score', 'N/A')}
- Error Rate: {data.get('session', {}).get('error_rate', 'N/A')}

Tools:
- Tool Latency P50: {data.get('tools', {}).get('tool_latency_p50', 'N/A')}ms
- Tool Latency P95: {data.get('tools', {}).get('tool_latency_p95', 'N/A')}ms
"""
                return [TextContent(type="text", text=metrics_text)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching metrics: {str(e)}")]

    async def _get_session_metrics(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get session metrics."""
        session_id = arguments.get("session_id")
        period = arguments.get("period", "24h")
        
        try:
            if session_id:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.layer2_url}{config.api_prefix}/sessions/{session_id}/analysis",
                        timeout=5.0,
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    metrics_text = f"""Session Metrics for {session_id}:

Total Conversations: {data.get('total_conversations', 0)}
Total Interactions: {data.get('total_interactions', 0)}
Average Acceptance Rate: {data.get('avg_acceptance_rate', 0) * 100:.1f}%
"""
                    return [TextContent(type="text", text=metrics_text)]
            else:
                # Get metrics for time period
                metrics = self.metrics_storage.get_latest_metrics(category="session")
                metrics_text = f"Session metrics for period {period}:\n{metrics}"
                return [TextContent(type="text", text=metrics_text)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching session metrics: {str(e)}")]

    async def _get_tool_performance(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get tool performance data."""
        tool_name = arguments.get("tool_name")
        period = arguments.get("period", "24h")
        
        try:
            if tool_name:
                # Get tool-specific metrics
                metrics = self.metrics_storage.get_latest_metrics(category=f"tools:{tool_name}")
                metrics_text = f"Tool performance for {tool_name}:\n{metrics}"
            else:
                # Get all tool metrics
                metrics = self.metrics_storage.get_latest_metrics(category="tools")
                metrics_text = f"All tool performance metrics:\n{metrics}"
            
            return [TextContent(type="text", text=metrics_text)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching tool performance: {str(e)}")]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main():
    """Main entry point for MCP server."""
    server = BlueplaneMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

