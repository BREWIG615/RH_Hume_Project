"""
Claude AI Client

Client for Anthropic Claude API with tool use support.
"""

from typing import Optional, Any
import logging
import os
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for Claude API interactions."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY")
        self.model = model
        self._client = None
    
    @property
    def client(self) -> Anthropic:
        if self._client is None:
            self._client = Anthropic(api_key=self.api_key)
        return self._client
    
    def complete(
        self,
        messages: list[dict],
        system: Optional[str] = None,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.1
    ) -> dict:
        """Send completion request to Claude."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = tools
        
        response = self.client.messages.create(**kwargs)
        return {
            "content": response.content,
            "stop_reason": response.stop_reason,
            "usage": {"input": response.usage.input_tokens, "output": response.usage.output_tokens}
        }
    
    def simple_complete(self, prompt: str, system: Optional[str] = None) -> str:
        """Simple text completion."""
        result = self.complete(
            messages=[{"role": "user", "content": prompt}],
            system=system
        )
        return result["content"][0].text if result["content"] else ""
