"""Execute Cypher Tool - Run graph queries against Neo4j."""

from src.agent.tools.base import BaseTool, ToolResult


class ExecuteCypherTool(BaseTool):
    """Tool to execute read-only Cypher queries."""
    
    def __init__(self, neo4j_client, config: dict):
        self.neo4j = neo4j_client
        self.config = config
        self.max_results = config.get("max_results", 100)
    
    @property
    def name(self) -> str:
        return "execute_cypher"
    
    @property
    def description(self) -> str:
        return (
            "Execute a read-only Cypher query against the Neo4j graph database. "
            "Use this for complex queries that aren't covered by other tools. "
            "Only SELECT/MATCH queries are allowed."
        )
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The Cypher query to execute (read-only)"
                },
                "parameters": {
                    "type": "object",
                    "description": "Optional query parameters",
                    "default": {}
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, query: str, parameters: dict = None) -> ToolResult:
        """Execute the Cypher query."""
        # Validate read-only
        query_upper = query.upper().strip()
        write_keywords = ["CREATE", "MERGE", "DELETE", "SET", "REMOVE", "DROP"]
        
        for keyword in write_keywords:
            if keyword in query_upper:
                return ToolResult(
                    success=False,
                    error=f"Write operations not allowed. Found: {keyword}"
                )
        
        try:
            results = self.neo4j.execute_cypher(query, parameters or {})
            
            # Limit results
            if len(results) > self.max_results:
                results = results[:self.max_results]
            
            return ToolResult(success=True, data=results)
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
