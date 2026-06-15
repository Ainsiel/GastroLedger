import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
GRIDWORK = ROOT / ".gridwork"


def test_frontend_issues_include_the_delivery_contract() -> None:
    violations: list[str] = []
    for path in (ROOT / "docs" / "backlog" / "issues").glob("*.md"):
        content = path.read_text(encoding="utf-8")
        if "- Frontend:" not in content:
            continue
        required = (
            "## Frontend Delivery Contract",
            "docs/backlog/frontend-delivery-contract.md",
            "shadcn/ui",
            "390, 1024 and 1440",
            "visual QA evidence",
        )
        missing = [marker for marker in required if marker not in content]
        if missing:
            violations.append(f"{path.relative_to(ROOT)} missing {missing}")

    assert not violations, "\n".join(violations)


def test_delivery_agents_reference_the_frontend_policy() -> None:
    agents = (
        "orchestrator",
        "planner-agent",
        "backlog-manager-agent",
        "implementer-agent",
        "verifier-agent",
    )
    violations: list[str] = []
    for agent in agents:
        manifest = json.loads(
            (GRIDWORK / "agents" / agent / "agent.json").read_text(encoding="utf-8")
        )
        if not any(
            reference.endswith("frontend-delivery-policy.md")
            for reference in manifest["policyRefs"]
        ):
            violations.append(agent)

    assert not violations, "\n".join(violations)


def test_delivery_workflows_enforce_frontend_readiness_and_verification() -> None:
    workflows = (
        "backlog-management",
        "backlog-task-delivery",
        "tdd-implementation",
        "verification-pr",
        "feature-pr-delivery",
    )
    violations = [
        workflow
        for workflow in workflows
        if "frontend-delivery-policy.md"
        not in (GRIDWORK / "workflows" / workflow / "WORKFLOW.md").read_text(
            encoding="utf-8"
        )
    ]

    assert not violations, "\n".join(violations)


def test_pull_request_template_requires_frontend_evidence() -> None:
    content = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")

    assert "approved UI Spec and shadcn/ui system" in content
    assert "390/1024/1440 visual QA evidence" in content
