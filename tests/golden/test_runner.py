"""
Golden Test Runner

Runs golden test cases to validate agent quality.
"""

from pathlib import Path
from typing import Optional
import logging
import yaml

import pytest

logger = logging.getLogger(__name__)


def load_test_cases(path: str = "tests/golden/test_cases.yaml") -> list[dict]:
    """Load test cases from YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("test_cases", [])


def evaluate_response(response: dict, expected: dict) -> dict:
    """
    Evaluate agent response against expected behavior.
    
    Returns:
        Dictionary with pass/fail and details
    """
    result = {
        "passed": True,
        "checks": [],
        "score": 0.0
    }
    
    # Check tools used
    if "tools_used" in expected:
        expected_tools = set(expected["tools_used"])
        actual_tools = set(response.get("tools_used", []))
        
        if expected_tools.issubset(actual_tools):
            result["checks"].append({"name": "tools_used", "passed": True})
        else:
            result["checks"].append({
                "name": "tools_used",
                "passed": False,
                "expected": list(expected_tools),
                "actual": list(actual_tools)
            })
            result["passed"] = False
    
    # Check minimum tools
    if "min_tools" in expected:
        actual_count = len(response.get("tools_used", []))
        if actual_count >= expected["min_tools"]:
            result["checks"].append({"name": "min_tools", "passed": True})
        else:
            result["checks"].append({
                "name": "min_tools",
                "passed": False,
                "expected": f">= {expected['min_tools']}",
                "actual": actual_count
            })
            result["passed"] = False
    
    # Check contains
    if "contains" in expected:
        answer = response.get("answer", "").lower()
        for term in expected["contains"]:
            if term.lower() in answer:
                result["checks"].append({"name": f"contains_{term}", "passed": True})
            else:
                result["checks"].append({
                    "name": f"contains_{term}",
                    "passed": False,
                    "message": f"Response should contain '{term}'"
                })
                result["passed"] = False
    
    # Check excludes
    if "excludes" in expected:
        answer = response.get("answer", "").lower()
        for term in expected["excludes"]:
            if term.lower() not in answer:
                result["checks"].append({"name": f"excludes_{term}", "passed": True})
            else:
                result["checks"].append({
                    "name": f"excludes_{term}",
                    "passed": False,
                    "message": f"Response should not contain '{term}'"
                })
                result["passed"] = False
    
    # Calculate score
    passed_checks = sum(1 for c in result["checks"] if c.get("passed"))
    total_checks = len(result["checks"])
    result["score"] = passed_checks / total_checks if total_checks > 0 else 1.0
    
    return result


class GoldenTestRunner:
    """Runner for golden test cases."""
    
    def __init__(self, agent, test_cases_path: str = "tests/golden/test_cases.yaml"):
        """
        Initialize runner.
        
        Args:
            agent: Agent instance to test
            test_cases_path: Path to test cases YAML
        """
        self.agent = agent
        self.test_cases = load_test_cases(test_cases_path)
    
    async def run_test(self, test_case: dict) -> dict:
        """Run a single test case."""
        query = test_case["query"]
        expected = test_case.get("expected", {})
        
        logger.info(f"Running test: {test_case['id']}")
        
        try:
            # Run agent
            result = await self.agent.run(query)
            
            # Evaluate response
            evaluation = evaluate_response(
                {
                    "answer": result.answer,
                    "tools_used": result.tools_used,
                },
                expected
            )
            
            return {
                "test_id": test_case["id"],
                "test_name": test_case["name"],
                "query": query,
                "response": result.answer,
                "tools_used": result.tools_used,
                "evaluation": evaluation,
                "passed": evaluation["passed"],
            }
            
        except Exception as e:
            logger.error(f"Test {test_case['id']} failed: {e}")
            return {
                "test_id": test_case["id"],
                "test_name": test_case["name"],
                "query": query,
                "error": str(e),
                "passed": False,
            }
    
    async def run_all(self, tags: Optional[list[str]] = None) -> dict:
        """
        Run all test cases.
        
        Args:
            tags: Optional tags to filter tests
            
        Returns:
            Summary of test results
        """
        # Filter by tags if specified
        if tags:
            cases = [
                tc for tc in self.test_cases
                if any(tag in tc.get("tags", []) for tag in tags)
            ]
        else:
            cases = self.test_cases
        
        results = []
        for test_case in cases:
            result = await self.run_test(test_case)
            results.append(result)
        
        # Summary
        passed = sum(1 for r in results if r["passed"])
        failed = len(results) - passed
        
        return {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(results) if results else 0,
            "results": results,
        }


# =============================================================================
# Pytest Fixtures and Tests
# =============================================================================

@pytest.fixture
def test_cases():
    """Load test cases."""
    return load_test_cases()


@pytest.mark.golden
@pytest.mark.asyncio
async def test_golden_basic(test_cases):
    """Run basic golden tests (placeholder)."""
    # TODO: Implement with real agent
    assert len(test_cases) > 0
    
    for tc in test_cases:
        assert "id" in tc
        assert "query" in tc
        assert "expected" in tc


if __name__ == "__main__":
    # Quick validation of test cases
    cases = load_test_cases()
    print(f"Loaded {len(cases)} test cases")
    
    for tc in cases:
        print(f"  - {tc['id']}: {tc['name']}")
