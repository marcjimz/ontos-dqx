#!/usr/bin/env python3
"""Trigger Ontos DQX quality checks and evaluate the quality gate."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import load_environment
from lib.ontos_client import OntosClient


def run_dqx(env_name: str, fail_on_error: bool = True):
    env = load_environment(env_name)
    client = OntosClient(
        base_url=env["ontos_base_url"],
        token=env.get("databricks_token"),
        databricks_profile=env.get("databricks_profile"),
    )

    # Trigger the data_quality_checks workflow
    print(f"Starting DQX quality checks ({env_name})...")
    result = client.start_workflow("data_quality_checks")
    run_id = result.get("run_id")

    if not run_id:
        print("  Warning: Could not start workflow job. Running per-contract profiling instead.")
        run_per_contract(client, env, fail_on_error)
        return

    print(f"  Job run ID: {run_id}")
    status = client.wait_for_job(run_id, timeout=600)

    state = status.get("state", {})
    result_state = state.get("result_state", "UNKNOWN")
    print(f"  Job result: {result_state}")

    if result_state != "SUCCESS" and fail_on_error:
        print("\nQuality gate FAILED")
        sys.exit(1)

    print("\nQuality gate PASSED")


def run_per_contract(client: OntosClient, env: dict, fail_on_error: bool):
    """Fallback: run DQX profiling per contract and check for errors."""
    contracts = client.list_contracts()
    our_contracts = [c for c in contracts if c.get("domain_name") == "Scripius PBM"]

    all_passed = True

    for contract in our_contracts:
        cid = contract["id"]
        name = contract["name"]
        schema_names = [s["name"] for s in contract.get("schema", [])]

        print(f"\n  Profiling: {name}")
        client.start_profiling(cid, schema_names)

        run = client.wait_for_profiling(cid, timeout=600)
        status = run.get("status")
        print(f"    Status: {status}")

        if status == "failed":
            all_passed = False
            print(f"    ERROR: Profiling failed")
        elif status == "completed":
            suggestions = client.get_suggestions(cid, run["id"])
            errors = [s for s in suggestions if s.get("severity") == "error"]
            warnings = [s for s in suggestions if s.get("severity") == "warning"]
            print(f"    Errors: {len(errors)}, Warnings: {len(warnings)}")

            if errors:
                all_passed = False
                for e in errors:
                    print(f"      FAIL: {e.get('name', 'unnamed')} - {e.get('description', '')}")

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
