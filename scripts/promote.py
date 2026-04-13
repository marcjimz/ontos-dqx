#!/usr/bin/env python3
"""Promote data and contracts from one environment to the next."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from deploy import deploy
from sync_contracts import sync_contracts
from run_dqx import run_dqx

PROMOTION_ORDER = {"dev": "qa", "qa": "prod"}


def promote(source_env: str):
    target_env = PROMOTION_ORDER.get(source_env)
    if not target_env:
        print(f"Error: No promotion target for '{source_env}'")
        sys.exit(1)

    print(f"=== Promoting {source_env} -> {target_env} ===\n")

    # 1. Deploy DDLs to target (no seed data for qa/prod)
    print("--- Step 1: Deploy DDL ---")
    deploy(target_env, seed=False)

    # 2. Sync contracts with target status
    print("\n--- Step 2: Sync ODCS contracts ---")
    sync_contracts(target_env)

    # 3. Run DQX quality gate
    print("\n--- Step 3: DQX quality gate ---")
    run_dqx(target_env, fail_on_error=True)

    print(f"\n=== Promotion to {target_env} complete ===")


def main():
    parser = argparse.ArgumentParser(description="Promote environment (DEV->QA or QA->PROD)")
    parser.add_argument("--source", required=True, choices=["dev", "qa"], help="Source environment")
    args = parser.parse_args()
    promote(args.source)


if __name__ == "__main__":
    main()
