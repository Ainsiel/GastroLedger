import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
API_PACKAGE = ROOT / "apps" / "api" / "gastroledger_api"
MODULES_ROOT = API_PACKAGE / "modules"
CONTEXTS = {
    "platform_organization",
    "menu_engineering",
    "procurement",
    "inventory_production",
    "store_operations",
    "control_insights",
}
FORBIDDEN_DOMAIN_IMPORTS = {"fastapi", "pydantic", "psycopg", "sqlalchemy", "starlette"}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_confirmed_contexts_expose_only_the_required_foundation_boundaries() -> None:
    assert {path.name for path in MODULES_ROOT.iterdir() if path.is_dir()} == CONTEXTS
    for context in CONTEXTS:
        context_root = MODULES_ROOT / context
        assert (context_root / "public.py").is_file()
        assert (context_root / "application" / "__init__.py").is_file()
        assert (context_root / "domain" / "__init__.py").is_file()


def test_domain_boundaries_do_not_import_frameworks_or_delivery_packages() -> None:
    forbidden_prefixes = FORBIDDEN_DOMAIN_IMPORTS | {
        "gastroledger_api.application",
        "gastroledger_api.composition",
        "gastroledger_api.technical",
    }
    violations: list[str] = []
    for path in MODULES_ROOT.glob("*/domain/**/*.py"):
        for imported in imported_modules(path):
            if any(
                imported == prefix or imported.startswith(f"{prefix}.")
                for prefix in forbidden_prefixes
            ):
                violations.append(f"{path.relative_to(ROOT)} imports {imported}")
    assert not violations, "\n".join(violations)


def test_contexts_never_import_another_context_internal_package() -> None:
    violations: list[str] = []
    for context in CONTEXTS:
        for path in (MODULES_ROOT / context).rglob("*.py"):
            for imported in imported_modules(path):
                prefix = "gastroledger_api.modules."
                if not imported.startswith(prefix):
                    continue
                target_parts = imported.removeprefix(prefix).split(".")
                target_context = target_parts[0]
                if target_context == context:
                    continue
                if len(target_parts) != 2 or target_parts[1] != "public":
                    violations.append(f"{path.relative_to(ROOT)} imports {imported}")
    assert not violations, "\n".join(violations)


def test_context_public_boundaries_do_not_import_frameworks() -> None:
    violations: list[str] = []
    for path in MODULES_ROOT.glob("*/public.py"):
        for imported in imported_modules(path):
            if imported.split(".")[0] in FORBIDDEN_DOMAIN_IMPORTS:
                violations.append(f"{path.relative_to(ROOT)} imports {imported}")
    assert not violations, "\n".join(violations)


def test_foundation_defers_context_adapters_and_repositories() -> None:
    forbidden = [
        path.relative_to(ROOT)
        for path in MODULES_ROOT.rglob("*")
        if "adapter" in path.name.lower() or "repository" in path.name.lower()
    ]
    assert not forbidden, "\n".join(str(path) for path in forbidden)


def test_composition_root_imports_contexts_through_public_boundaries() -> None:
    imports = imported_modules(API_PACKAGE / "composition.py")
    context_imports = {item for item in imports if item.startswith("gastroledger_api.modules.")}
    expected = {f"gastroledger_api.modules.{context}.public" for context in CONTEXTS}
    assert context_imports == expected


def test_fastapi_routes_import_contexts_through_public_boundaries() -> None:
    violations: list[str] = []
    for path in (API_PACKAGE / "technical").glob("*routes.py"):
        for imported in imported_modules(path):
            prefix = "gastroledger_api.modules."
            if imported.startswith(prefix) and not imported.endswith(".public"):
                violations.append(f"{path.relative_to(ROOT)} imports {imported}")
    assert not violations, "\n".join(violations)


def test_no_external_http_client_dependency_is_declared() -> None:
    requirements = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "apps" / "api").glob("requirements*.txt")
    ).lower()
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    workspace = json.loads((ROOT / "apps" / "web" / "package.json").read_text(encoding="utf-8"))
    node_dependencies = {
        **package.get("dependencies", {}),
        **package.get("devDependencies", {}),
        **workspace.get("dependencies", {}),
        **workspace.get("devDependencies", {}),
    }

    python_dependencies = set(re.findall(r"(?m)^\s*([A-Za-z0-9_-]+)", requirements))
    assert not {"requests", "httpx", "aiohttp"} & python_dependencies
    assert not {"axios", "got", "ky", "node-fetch"} & set(node_dependencies)


def test_sqlalchemy_is_confined_to_technical_persistence_adapters() -> None:
    violations: list[str] = []
    for path in API_PACKAGE.rglob("*.py"):
        if "sqlalchemy" not in imported_modules(path):
            continue
        if "technical" not in path.relative_to(API_PACKAGE).parts:
            violations.append(str(path.relative_to(ROOT)))
    assert not violations, "\n".join(violations)
