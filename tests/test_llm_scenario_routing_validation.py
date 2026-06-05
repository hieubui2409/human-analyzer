"""Validate LLM scenario routing against hybrid orc-intake routing script.

Hybrid design: keyword+phrase pre-filter for fast routing. When confidence
< 0.5, returns AMBIGUOUS with suggestions so LLM makes final decision.

Tests validate:
1. High-confidence scenarios route correctly via keywords+phrases
2. Low-confidence scenarios return AMBIGUOUS with correct best_domain
3. Coverage: all domains have scenarios, all scenarios have validation
"""
import json
import subprocess
import os
from pathlib import Path

import pytest
import yaml
from venv_python import VENV_PYTHON

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(VENV_PYTHON)
SCENARIOS_FILE = PROJECT_ROOT / "tests" / "scenarios" / "llm-reasoning-scenarios.yaml"
ROUTE_SCRIPT = (
    PROJECT_ROOT / ".claude" / "skills" / "orc-intake" / "scripts"
    / "route-task-to-framework-domain.py"
)
ENV = {
    **os.environ,
    "PYTHONPATH": str(PROJECT_ROOT / ".claude" / "scripts"),
    "MOCK_DATA_DIR": str(PROJECT_ROOT / "tests" / "mock-data"),
}


def load_scenarios():
    with open(SCENARIOS_FILE) as f:
        data = yaml.safe_load(f)
    scenarios = []
    for cat_scenarios in data["categories"].values():
        for s in cat_scenarios:
            scenarios.append(s)
    return scenarios


ALL_SCENARIOS = load_scenarios()
# Domain-routing test applies only to scenarios that declare expected_route.
# Orchestration scenarios (e.g. R3/R4) carry expected_skills instead and are
# covered by TestRoutingCoverage, not the keyword router parametrization.
ROUTING_SCENARIOS = [s for s in ALL_SCENARIOS if s.get("expected_route") is not None]


def route_task(description: str) -> dict:
    result = subprocess.run(
        [PYTHON, str(ROUTE_SCRIPT), "--json", description],
        capture_output=True, text=True, timeout=30, env=ENV,
    )
    assert result.returncode == 0, f"Route script failed: {result.stderr}"
    return json.loads(result.stdout)


@pytest.mark.parametrize(
    "scenario",
    ROUTING_SCENARIOS,
    ids=[f"{s['id']}-{s['name']}" for s in ROUTING_SCENARIOS],
)
def test_scenario_routing(scenario):
    """Each scenario's expected domain should appear as domain or best_domain."""
    expected = scenario["expected_route"]

    result = route_task(scenario["input"])
    actual = result["domain"]
    best = result.get("best_domain", actual)
    expected_list = expected if isinstance(expected, list) else [expected]

    if actual == "AMBIGUOUS":
        assert best in expected_list, (
            f"{scenario['id']}: AMBIGUOUS, best_domain={best}, "
            f"expected one of {expected_list}. Scores: {result['all_scores']}"
        )
    elif actual == "UNKNOWN":
        pytest.skip(
            f"{scenario['id']}: UNKNOWN — no keyword signal. "
            f"Requires pure LLM semantic routing."
        )
    else:
        assert actual in expected_list, (
            f"{scenario['id']}: routed to {actual}, "
            f"expected {expected_list}. Scores: {result['all_scores']}"
        )


class TestRoutingCoverage:
    def test_all_domains_have_scenarios(self):
        routes = set()
        for s in ALL_SCENARIOS:
            route = s.get("expected_route")
            if route is None:
                continue
            if isinstance(route, list):
                routes.update(route)
            else:
                routes.add(route)
        for domain in ["MAT", "PSY", "CRE"]:
            assert domain in routes, f"No scenario targets {domain}"

    def test_scenario_count(self):
        assert len(ALL_SCENARIOS) >= 30

    def test_all_scenarios_have_validation(self):
        with open(SCENARIOS_FILE) as f:
            data = yaml.safe_load(f)
        for cat_scenarios in data["categories"].values():
            for s in cat_scenarios:
                assert "validation" in s, f"{s['id']} missing validation"
                assert len(s["validation"]) > 0, f"{s['id']} empty validation"

    def test_no_unknown_routes(self):
        """All scenarios should have at least some keyword signal (not UNKNOWN)."""
        unknown = []
        for s in ALL_SCENARIOS:
            expected = s.get("expected_route")
            if expected is None:
                continue
            result = route_task(s["input"])
            if result["domain"] == "UNKNOWN":
                unknown.append(s["id"])
        assert len(unknown) == 0, (
            f"{len(unknown)} scenarios routed UNKNOWN (no keyword signal): {unknown}"
        )

    def test_high_confidence_accuracy(self):
        """High-confidence routes (not AMBIGUOUS) should be >=80% correct."""
        correct = 0
        total = 0
        for s in ALL_SCENARIOS:
            expected = s.get("expected_route")
            if expected is None:
                continue
            result = route_task(s["input"])
            if result["domain"] not in ("AMBIGUOUS", "UNKNOWN"):
                total += 1
                expected_list = expected if isinstance(expected, list) else [expected]
                if result["domain"] in expected_list:
                    correct += 1
        if total == 0:
            pytest.skip("No high-confidence routes to measure")
        accuracy = correct / total
        assert accuracy >= 0.80, (
            f"High-confidence accuracy {accuracy:.0%} < 80% ({correct}/{total})"
        )
