"""Facility Tools - Get facility status and details."""

from src.agent.tools.base import BaseTool, ToolResult


class GetFacilityStatusTool(BaseTool):
    """Tool to get facility status and details."""
    
    def __init__(self, neo4j_client, config: dict):
        self.neo4j = neo4j_client
        self.config = config
    
    @property
    def name(self) -> str:
        return "get_facility_status"
    
    @property
    def description(self) -> str:
        return (
            "Get the current status of a facility including operational status, "
            "asset counts by readiness, inventory summary, and emotional indicators. "
            "Use when asked about a specific facility's health or status."
        )
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "facility_name": {
                    "type": "string",
                    "description": "Name of the facility (e.g., 'Yokosuka', 'Kadena')"
                },
                "facility_id": {
                    "type": "string",
                    "description": "ID of the facility (alternative to name)"
                }
            }
        }
    
    async def execute(self, facility_name: str = None, facility_id: str = None) -> ToolResult:
        """Get facility status."""
        if not facility_name and not facility_id:
            return ToolResult(success=False, error="Must provide facility_name or facility_id")
        
        # TODO: Implement query
        query = """
        MATCH (f:Facility)
        WHERE f.name = $name OR f.id = $id
        OPTIONAL MATCH (a:Asset)-[:STATIONED_AT]->(f)
        WITH f, 
             count(a) as total_assets,
             sum(CASE WHEN a.status = 'FMC' THEN 1 ELSE 0 END) as fmc_count,
             sum(CASE WHEN a.status IN ['NMCM', 'NMCS'] THEN 1 ELSE 0 END) as nmc_count
        RETURN f, total_assets, fmc_count, nmc_count
        """
        
        try:
            results = self.neo4j.execute_cypher(query, {
                "name": facility_name,
                "id": facility_id
            })
            
            if not results:
                return ToolResult(success=False, error="Facility not found")
            
            return ToolResult(success=True, data=results[0])
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
