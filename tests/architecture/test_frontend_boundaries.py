import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
WEB_ROOT = ROOT / "apps" / "web"
FEATURES_ROOT = WEB_ROOT / "features"
ROUTE_OWNERS = {
    "app/(public)/register/layout.tsx": "onboarding",
    "app/(public)/login/layout.tsx": "onboarding",
    "app/(app)/dashboard/layout.tsx": "platform-admin",
    "app/(app)/settings/layout.tsx": "platform-admin",
    "app/(app)/menu/layout.tsx": "menu-engineering",
    "app/(app)/procurement/layout.tsx": "procurement",
    "app/(app)/inventory/layout.tsx": "inventory-production",
    "app/(app)/operations/layout.tsx": "store-operations",
    "app/(app)/control/layout.tsx": "control-insights",
}


def source_files() -> list[Path]:
    return [
        path
        for path in WEB_ROOT.rglob("*")
        if path.suffix in {".ts", ".tsx"}
        and ".next" not in path.parts
        and "node_modules" not in path.parts
    ]


def test_each_approved_route_imports_its_feature_public_surface() -> None:
    for route, feature in ROUTE_OWNERS.items():
        route_path = WEB_ROOT / route
        assert route_path.is_file()
        assert f'from "@/features/{feature}"' in route_path.read_text(encoding="utf-8")
        assert (FEATURES_ROOT / feature / "index.ts").is_file()


def test_features_do_not_import_another_feature() -> None:
    violations: list[str] = []
    pattern = re.compile(r'from ["\']@/features/([^/"\']+)')
    for path in FEATURES_ROOT.rglob("*.ts*"):
        owner = path.relative_to(FEATURES_ROOT).parts[0]
        for target in pattern.findall(path.read_text(encoding="utf-8")):
            if target != owner:
                violations.append(f"{path.relative_to(ROOT)} imports feature {target}")
    assert not violations, "\n".join(violations)


def test_frontend_does_not_import_backend_source() -> None:
    violations = [
        str(path.relative_to(ROOT))
        for path in source_files()
        if "gastroledger_api" in path.read_text(encoding="utf-8")
        or "apps/api" in path.read_text(encoding="utf-8")
    ]
    assert not violations, "\n".join(violations)


def test_foundation_contains_no_html_artifact() -> None:
    foundation_roots = [ROOT / path for path in ("apps", "packages", "tests", "infra")]
    assert not [
        path
        for foundation_root in foundation_roots
        for path in foundation_root.rglob("*.html")
        if ".next" not in path.parts and "node_modules" not in path.parts
    ]
