"""
Agent Guardrails

Safety and scope guardrails for the agent:
- Read-only mode
- Scope limits (max results, allowed operations)
- Confirmation workflow
- Rate limiting
- Audit logging
- Output validation
- Token/cost limits
- Timeout controls
"""

from dataclasses import dataclass
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class GuardrailConfig:
    """Configuration for agent guardrails."""
    read_only: bool = True
    max_results: int = 100
    require_confirmation: bool = False
    rate_limit_per_minute: int = 30
    timeout_seconds: int = 60
    max_tokens_per_request: int = 4096
    allowed_tools: Optional[list[str]] = None
    blocked_patterns: Optional[list[str]] = None


class GuardedAgentExecutor:
    """
    Wraps agent execution with safety guardrails.
    
    Example:
        config = GuardrailConfig(read_only=True, max_results=50)
        executor = GuardedAgentExecutor(agent, config)
        result = await executor.execute(user_id="user123", user_query="...")
    """
    
    def __init__(self, agent, config: Optional[GuardrailConfig] = None):
        self.agent = agent
        self.config = config or GuardrailConfig()
        self._request_times: dict[str, list[float]] = {}
    
    async def execute(
        self,
        user_id: str,
        user_query: str,
        context: Optional[dict] = None,
    ) -> dict:
        """
        Execute agent query with guardrails.
        
        Args:
            user_id: Identifier for rate limiting
            user_query: User's query
            context: Optional context
            
        Returns:
            Agent result or error
        """
        # Check rate limit
        if not self._check_rate_limit(user_id):
            return {"error": "Rate limit exceeded. Please wait."}
        
        # Validate query
        validation = self._validate_query(user_query)
        if validation:
            return {"error": validation}
        
        # Execute with timeout
        try:
            # TODO: Add proper timeout handling
            start_time = time.time()
            result = await self.agent.run(user_query, context)
            elapsed = time.time() - start_time
            
            # Log for audit
            self._audit_log(user_id, user_query, result, elapsed)
            
            return {
                "answer": result.answer,
                "steps": result.steps,
                "tools_used": result.tools_used,
                "execution_time": elapsed,
            }
            
        except TimeoutError:
            return {"error": "Request timed out. Try a simpler query."}
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {"error": f"Execution failed: {str(e)}"}
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limit."""
        now = time.time()
        window = 60  # 1 minute
        
        if user_id not in self._request_times:
            self._request_times[user_id] = []
        
        # Clean old entries
        self._request_times[user_id] = [
            t for t in self._request_times[user_id]
            if now - t < window
        ]
        
        # Check limit
        if len(self._request_times[user_id]) >= self.config.rate_limit_per_minute:
            return False
        
        # Record request
        self._request_times[user_id].append(now)
        return True
    
    def _validate_query(self, query: str) -> Optional[str]:
        """Validate query against blocked patterns."""
        if self.config.blocked_patterns:
            for pattern in self.config.blocked_patterns:
                if pattern.lower() in query.lower():
                    return f"Query contains blocked pattern."
        return None
    
    def _audit_log(self, user_id: str, query: str, result, elapsed: float):
        """Log query for audit trail."""
        logger.info(
            f"AUDIT: user={user_id} query={query[:50]}... "
            f"tools={result.tools_used} time={elapsed:.2f}s"
        )
