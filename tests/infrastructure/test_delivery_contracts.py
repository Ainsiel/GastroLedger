from pathlib import Path

ROOT = Path(__file__).parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def workflow(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_required_aggregate_checks_are_stable() -> None:
    required = {
        "feature-pr.yml": ("name: feature", "name: regression-gate"),
        "develop.yml": ("name: develop", "name: integration-gate"),
        "release-pr.yml": ("name: release", "name: full-regression-gate"),
        "production.yml": ("name: production", "name: smoke-gate"),
    }
    for filename, markers in required.items():
        content = workflow(filename)
        assert all(marker in content for marker in markers)


def test_workflows_use_read_only_permissions_and_no_secrets() -> None:
    violations: list[str] = []
    forbidden = ("contents: write", "write-all", "GH_TOKEN", "GITHUB_TOKEN")
    for path in WORKFLOWS.glob("*.yml"):
        content = path.read_text(encoding="utf-8")
        if "contents: read" not in content:
            violations.append(f"{path.name} has no read-only contents permission")
        violations.extend(
            f"{path.name} contains {marker}" for marker in forbidden if marker in content
        )
        if path.name != "production.yml" and "secrets." in content:
            violations.append(f"{path.name} contains secrets outside production deploy")
    assert not violations, "\n".join(violations)


def test_production_workflow_deploys_to_ec2_after_smoke() -> None:
    content = workflow("production.yml")
    required = (
        "branches:\n      - main",
        "name: deploy-ec2",
        "needs:\n      - artifact-smoke",
        "AWS_EC2_SSH_PRIVATE_KEY",
        "REPOSITORY_URL=https://github.com/Ainsiel/GastroLedger.git",
        "sudo dnf install -y git docker nginx python3",
        "COMPOSE_URL=",
        "sudo docker compose version",
        "/usr/local/lib/docker/cli-plugins",
        "docker/compose/releases/latest/download/docker-compose-linux-$ARCH",
        "ssh-keyscan",
        "git reset --hard origin/main",
        "COMPOSE=\"sudo docker compose",
        "run --rm migrate",
        "run --rm seed",
        "up --detach --wait web api worker",
    )
    assert all(marker in content for marker in required)


def test_release_contract_enables_full_suite() -> None:
    content = workflow("release-pr.yml")
    assert "build_containers: true" in content
    assert "run_e2e: true" in content
    assert "run_migrations: true" in content


def test_compose_declares_only_approved_services() -> None:
    content = (ROOT / "infra" / "compose" / "compose.yaml").read_text(encoding="utf-8")
    for service in ("web", "api", "worker", "postgres", "migrate", "seed"):
        assert f"  {service}:" in content
    for forbidden in ("redis:", "broker:", "rabbitmq:", "kafka:", "external-api:"):
        assert forbidden not in content.lower()


def test_develop_web_syncs_dependencies_and_cache_before_starting_nextjs() -> None:
    content = (ROOT / "infra" / "compose" / "compose.develop.yaml").read_text(
        encoding="utf-8"
    )

    assert (
        'command: sh -c "npm ci && rm -rf apps/web/.next/* '
        '&& npm --workspace @gastroledger/web run dev"'
    ) in content


def test_foundation_migration_contains_no_functional_schema() -> None:
    content = (ROOT / "infra" / "migrations" / "0000-foundation.sql").read_text(
        encoding="utf-8"
    )
    normalized = content.lower()
    assert not [
        statement
        for statement in ("create table", "alter table", "drop table", "create extension")
        if statement in normalized
    ]


def test_no_insecure_placeholder_is_committed_to_delivery_files() -> None:
    delivery_files = [
        ROOT / "infra" / "compose" / ".env.example",
        ROOT / "infra" / "compose" / "compose.yaml",
        *WORKFLOWS.glob("*.yml"),
    ]
    forbidden = ("replace-with", "changeme", "password123", "todo-secret")
    violations = [
        f"{path.relative_to(ROOT)} contains {marker}"
        for path in delivery_files
        for marker in forbidden
        if marker in path.read_text(encoding="utf-8").lower()
    ]
    assert not violations, "\n".join(violations)
