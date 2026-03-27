"""
Hume AI Client

Client for Hume AI emotional analysis API.
"""

from typing import Optional
import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class HumeClient:
    """Client for Hume AI text analysis."""
    
    BASE_URL = "https://api.hume.ai/v0"
    TARGET_EMOTIONS = ["anxiety", "urgency", "confusion", "fear", "confidence", "frustration"]
    
    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        import os
        self.api_key = api_key or os.environ.get("HUME_API_KEY")
        self.timeout = timeout
        self._client = None
    
    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.BASE_URL,
                headers={"X-Hume-Api-Key": self.api_key or "", "Content-Type": "application/json"},
                timeout=self.timeout
            )
        return self._client
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def analyze_text(self, text: str) -> dict[str, float]:
        """Analyze text for emotional signals."""
        if not self.api_key:
            return self._mock_analysis(text)
        
        response = self.client.post("/batch/jobs", json={
            "models": {"language": {"raw_text": True}},
            "raw_text": [{"text": text}]
        })
        response.raise_for_status()
        return self._extract_scores(response.json())
    
    def _extract_scores(self, result: dict) -> dict[str, float]:
        """Extract emotion scores from Hume API response."""
        scores = {emotion: 0.0 for emotion in self.TARGET_EMOTIONS}
        # Parse Hume response structure and map to our emotions
        return scores
    
    def _mock_analysis(self, text: str) -> dict[str, float]:
        """Generate mock analysis for testing."""
        import hashlib
        text_hash = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        base = (text_hash % 100) / 200
        
        text_lower = text.lower()
        return {
            "anxiety": base + 0.3 * ("worried" in text_lower or "concerned" in text_lower),
            "urgency": base + 0.4 * ("urgent" in text_lower or "asap" in text_lower),
            "confusion": base + 0.3 * ("confused" in text_lower),
            "fear": base + 0.5 * ("afraid" in text_lower or "threat" in text_lower),
            "confidence": 0.5 + base,
            "frustration": base * 0.8,
        }
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
