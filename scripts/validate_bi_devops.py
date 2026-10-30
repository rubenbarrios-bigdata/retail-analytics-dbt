"""
Automated BI DevOps & Analytics Engineering CI Validation Suite.
Validates:
  1. Security & Git hygiene (zero leaked credentials or binary .abf caches).
  2. dbt Core project structure, seeds, SQL models, and YAML data quality tests.
  3. Power BI Project (PBIP / PBIR) JSON files and custom executive theme.
  4. Microsoft Fabric Git Integration (.platform v2.0.0) manifests.
  5. Tabular Model Definition Language (TMDL) tables, relationships, and DAX KPIs.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent


def fail(msg: str) -> None:
    print(f"[ERROR] {msg}")
    sys.exit(1)


def check_security_hygiene() -> None:
    # Ensure no git-tracked credentials or .abf binary caches exist
    forbidden_patterns = ["*credentials*.json", "*service-account*.json", "profiles.yml", "*.abf"]
    matches: list[str] = []
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in {".venv", ".git", ".pbi", "target", "dbt_packages"}]
        for fname in files:
            for pattern in forbidden_patterns:
                if fnmatch.fnmatch(fname.lower(), pattern.lower()):
                    matches.append(str(Path(root, fname).relative_to(REPO_ROOT)))
    if matches:
        fail(f"Forbidden file(s) detected: {matches}")

    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    for required_rule in ["powerbi/**/.pbi/cache.abf", "profiles.yml"]:
        if required_rule not in gitignore_text:
            fail(f"Missing critical security/PBIP rule '{required_rule}' in .gitignore")
    print("[OK] Security & Git hygiene verified (.gitignore rules active, zero leaked credentials).")


def check_dbt_project() -> None:
    dbt_proj_path = REPO_ROOT / "dbt_project.yml"
    if not dbt_proj_path.exists():
        fail("Missing dbt_project.yml")

    proj_text = dbt_proj_path.read_text(encoding="utf-8")
    if yaml is not None:
        dbt_cfg = yaml.safe_load(proj_text)
        if dbt_cfg.get("name") != "retail_analytics":
            fail("Unexpected project name in dbt_project.yml")
    elif "retail_analytics" not in proj_text:
        fail("Unexpected project name in dbt_project.yml")

    expected_seeds = [
        "raw_customers.csv",
        "raw_products.csv",
        "raw_orders.csv",
        "raw_order_items.csv",
    ]
    for seed in expected_seeds:
        if not (REPO_ROOT / "seeds" / seed).exists():
            fail(f"Missing dbt seed file: seeds/{seed}")

    expected_models = [
        "models/staging/stg_customers.sql",
        "models/staging/stg_products.sql",
        "models/staging/stg_orders.sql",
        "models/staging/stg_order_items.sql",
        "models/marts/fct_orders.sql",
        "models/marts/dim_customers.sql",
        "models/marts/dim_products.sql",
    ]
    for model in expected_models:
        if not (REPO_ROOT / model).exists():
            fail(f"Missing dbt SQL model: {model}")

    total_tests = 0
    for schema_rel in ["models/staging/schema.yml", "models/marts/schema.yml"]:
        schema_path = REPO_ROOT / schema_rel
        if not schema_path.exists():
            fail(f"Missing dbt schema file: {schema_rel}")
        raw_schema = schema_path.read_text(encoding="utf-8")
        if yaml is not None:
            schema_data = yaml.safe_load(raw_schema)
            for model_entry in schema_data.get("models", []):
                for col in model_entry.get("columns", []):
                    total_tests += len(col.get("tests", []))
        else:
            total_tests += len(
                re.findall(r"^\s*-\s+(unique|not_null|relationships|accepted_values)\b", raw_schema, re.M)
            )

    if total_tests < 28:
        fail(f"Expected at least 28 dbt schema tests, found {total_tests}")
    print(f"[OK] dbt Core structure verified (4 seeds, 7 SQL models, {total_tests} YAML tests).")


def check_pbip_and_fabric_manifests() -> None:
    pbi_dir = REPO_ROOT / "powerbi"
    pbip_file = pbi_dir / "Dashboard dbt-BigQuery Retail Analytics.pbip"
    if not pbip_file.exists():
        fail("Missing .pbip root file in powerbi/")

    json_files = list(pbi_dir.rglob("*.json")) + list(pbi_dir.rglob("*.pbip")) + list(
        pbi_dir.rglob("*.pbism")
    ) + list(pbi_dir.rglob("*.pbir")) + list(pbi_dir.rglob(".platform"))

    if not json_files:
        fail("No PBIP/PBIR metadata files found in powerbi/")

    platform_count = 0
    for jf in json_files:
        if ".pbi" in jf.parts:
            continue
        try:
            data = json.loads(jf.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            fail(f"Invalid JSON syntax in {jf.relative_to(REPO_ROOT)}: {exc}")

        if jf.name == ".platform":
            platform_count += 1
            schema_url = data.get("$schema", "")
            if "fabric/gitIntegration/platformProperties" not in schema_url:
                fail(f"Invalid Fabric Git Integration schema in {jf.relative_to(REPO_ROOT)}")
            if not data.get("config", {}).get("logicalId"):
                fail(f"Missing logicalId in {jf.relative_to(REPO_ROOT)}")

    if platform_count < 2:
        fail(f"Expected 2 Microsoft Fabric .platform manifests (Report & SemanticModel), found {platform_count}")

    print(
        f"[OK] PBIP/PBIR JSON integrity & {platform_count} Microsoft Fabric Git Integration (.platform) manifests verified."
    )


def check_tmdl_semantic_model() -> None:
    def_dir = (
        REPO_ROOT
        / "powerbi"
        / "Dashboard dbt-BigQuery Retail Analytics.SemanticModel"
        / "definition"
    )
    for core_tmdl in ["database.tmdl", "model.tmdl", "relationships.tmdl"]:
        if not (def_dir / core_tmdl).exists():
            fail(f"Missing core TMDL file: {core_tmdl}")

    expected_tables = [
        "Calendario.tmdl",
        "Canales.tmdl",
        "Estados.tmdl",
        "dim_customers.tmdl",
        "dim_products.tmdl",
        "fct_orders.tmdl",
        "stg_order_items.tmdl",
    ]
    for tbl in expected_tables:
        if not (def_dir / "tables" / tbl).exists():
            fail(f"Missing TMDL table definition: tables/{tbl}")

    fct_text = (def_dir / "tables" / "fct_orders.tmdl").read_text(encoding="utf-8-sig")
    required_measures = [
        "Venta Neta",
        "Utilidad Neta",
        "% Margen Neto",
        "Ticket Promedio",
        "Pedidos Efectivos",
        "Unidades Vendidas",
    ]
    for measure in required_measures:
        if measure not in fct_text:
            fail(f"Missing executive DAX measure '{measure}' in fct_orders.tmdl")

    rel_text = (def_dir / "relationships.tmdl").read_text(encoding="utf-8-sig")
    rel_count = rel_text.count("relationship ")
    if rel_count < 6:
        fail(f"Expected 6 star-schema relationships in relationships.tmdl, found {rel_count}")

    print(
        f"[OK] TMDL Semantic Model verified (7 tables, {rel_count} Star Schema relationships, core DAX KPIs present)."
    )


def main() -> None:
    print("=== Running Retail Analytics & Power BI DevOps CI Validation ===")
    check_security_hygiene()
    check_dbt_project()
    check_pbip_and_fabric_manifests()
    check_tmdl_semantic_model()
    print("=== ALL BI DEVOPS & DBT CI CHECKS PASSED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
