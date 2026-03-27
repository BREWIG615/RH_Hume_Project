"""
Agent Tools

The 9 core tools available to the agent:
1. execute_cypher - Run graph queries
2. get_facility_status - Facility details
3. get_asset_status - Asset details
4. get_route_status - Route details
5. calculate_inventory_runway - Supply runway
6. find_alternate_routes - Route alternatives
7. get_pending_alerts - Alert queue
8. generate_report - Templated reports
9. get_emotional_summary - Hume aggregates
"""

from src.agent.tools.base import BaseTool, ToolResult
from src.agent.tools.cypher_tools import ExecuteCypherTool
from src.agent.tools.facility_tools import GetFacilityStatusTool
from src.agent.tools.asset_tools import GetAssetStatusTool
from src.agent.tools.route_tools import GetRouteStatusTool, FindAlternateRoutesTool
from src.agent.tools.inventory_tools import CalculateInventoryRunwayTool
from src.agent.tools.alert_tools import GetPendingAlertsTool
from src.agent.tools.report_tools import GenerateReportTool
from src.agent.tools.emotional_tools import GetEmotionalSummaryTool

__all__ = [
    "BaseTool",
    "ToolResult",
    "ExecuteCypherTool",
    "GetFacilityStatusTool",
    "GetAssetStatusTool",
    "GetRouteStatusTool",
    "FindAlternateRoutesTool",
    "CalculateInventoryRunwayTool",
    "GetPendingAlertsTool",
    "GenerateReportTool",
    "GetEmotionalSummaryTool",
]


def get_all_tools(neo4j_client, config: dict) -> list[BaseTool]:
    """Create all agent tools with dependencies."""
    return [
        ExecuteCypherTool(neo4j_client, config),
        GetFacilityStatusTool(neo4j_client, config),
        GetAssetStatusTool(neo4j_client, config),
        GetRouteStatusTool(neo4j_client, config),
        FindAlternateRoutesTool(neo4j_client, config),
        CalculateInventoryRunwayTool(neo4j_client, config),
        GetPendingAlertsTool(neo4j_client, config),
        GenerateReportTool(neo4j_client, config),
        GetEmotionalSummaryTool(neo4j_client, config),
    ]
