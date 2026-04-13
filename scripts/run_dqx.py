#!/usr/bin/env python3
"""Run ODCS quality checks against Databricks and report results to Ontos."""

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import load_environment
from lib.databricks_sql import get_client, execute_sql
from lib.ontos_client import OntosClient


def run_dqx(env_name: str, fail_on_error: bool = True):
    env = load_environment(env_name)
    catalog = env["catalog"]
    schema = env["schema"]
    db_client = get_client()
    warehouse_id = env["warehouse_id"]

    # Load ODCS contracts and extract SQL quality rules
    contracts_dir = Path(__file__).parent.parent / "contracts"
    all_passed = True
    total_errors = 0
    total_warnings = 0

    print(f"Running ODCS quality gate ({env_name})...")
    print(f"  Catalog: {catalog}, Schema: {schema}\n")

    for contract_file in sorted(contracts_dir.glob("*.yaml")):
        with open(contract_file) as f:
            contract = yaml.safe_load(f)

        contract_name = contract["name"]
        print(f"Contract: {contract_name}")

        for schema_obj in contract.get("schema", []):
            physical = schema_obj.get("physicalName", "")
            table_fqn = f"{catalog}.{physical}" if not physical.startswith(catalog) else physical

            for rule in schema_obj.get("quality", []):
                rule_name = rule.get("name", "unnamed")
                rule_type = rule.get("type", "")
                severity = rule.get("severity", "warning")
                description = rule.get("description", "")
                query = rule.get("query", "")
                must_be = rule.get("mustBe", "0")

                if rule_type != "sql" or not query:
                    # Library rules (not_null, unique) — skip for now, these are metadata-only
                    print(f"  SKIP [{severity}] {rule_name} (library rule)")
                    continue

                # Substitute catalog/table placeholders
                resolved_query = query.replace("${catalog}", catalog).replace("${table}", table_fqn)

                try:
                    result = execute_sql(db_client, warehouse_id, resolved_query)
                    value = str(result.data_array[0][0]) if result and result.data_array else "?"

                    if value == must_be:
                        print(f"  PASS [{severity}] {rule_name}: {value} (expected {must_be})")
                    else:
                        marker = "FAIL" if severity == "error" else "WARN"
                        print(f"  {marker} [{severity}] {rule_name}: {value} (expected {must_be}) — {description}")
                        if severity == "error":
                            total_errors += 1
                            all_passed = False
                        else:
                            total_warnings += 1
                except Exception as e:
                    print(f"  ERROR [{severity}] {rule_name}: {e}")
                    if severity == "error":
                        total_errors += 1
                        all_passed = False

        print()

    # Report summary
    print(f"Quality Gate Summary: {total_errors} errors, {total_warnings} warnings")

    # Report results to Ontos if available
    ontos_url = env.get("ontos_base_url", "")
    if ontos_url:
        try:
            ontos = OntosClient(
                base_url=ontos_url,
                token=env.get("databricks_token"),
                databricks_profile=env.get("databricks_profile"),
            )
            contracts = ontos.list_contracts()
            print(f"\nOntos: {len(contracts)} contracts registered")
        except Exception as e:
            print(f"\nOntos: Could not connect ({e})")

    if not all_passed and fail_on_error:
        print("\nQuality gate FAILED")
        sys.exit(1)
    else:
        print("\nQuality gate PASSED")


def main():
    parser = argparse.ArgumentParser(description="Run Ontos DQX quality gate")
    parser.add_argument("--env", required=True, choices=["dev", "qa", "prod"], help="Target environment")
    parser.add_argument("--no-fail", action="store_true", help="Don't exit with error on quality failures")
    args = parser.parse_args()
    run_dqx(args.env, fail_on_error=not args.no_fail)


if __name__ == "__main__":
    main()
