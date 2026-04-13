#!/usr/bin/env python3
"""Sync ODCS contracts from git to Ontos for a target environment."""

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from lib.config import load_environment
from lib.ontos_client import OntosClient


def sync_contracts(env_name: str):
    env = load_environment(env_name)
    catalog = env["catalog"]
    target_status = env["contract_status"]

    client = OntosClient(
        base_url=env["ontos_base_url"],
        token=env.get("databricks_token"),
        databricks_profile=env.get("databricks_profile"),
    )

    # Get existing contracts to decide create vs update
    existing = {c["name"]: c for c in client.list_contracts()}

    contracts_dir = Path(__file__).parent.parent / "contracts"
    for contract_file in sorted(contracts_dir.glob("*.yaml")):
        with open(contract_file) as f:
            contract = yaml.safe_load(f)

        # Adjust physical names to include this environment's catalog
        for schema_obj in contract.get("schema", []):
            physical = schema_obj.get("physicalName", "")
            if not physical.startswith(catalog):
                schema_obj["physicalName"] = f"{catalog}.{physical}"

            # Also substitute ${catalog} in quality rule queries
            for rule in schema_obj.get("quality", []):
                query = rule.get("query", "")
                if query:
                    rule["query"] = query.replace("${catalog}", catalog).replace("${table}", f"{catalog}.{physical}")

        # Set contract status for this environment tier
        contract["status"] = target_status

        name = contract["name"]
        if name in existing:
            print(f"  Updating: {name} -> {target_status}")
            client.update_contract(existing[name]["id"], contract)
        else:
            print(f"  Creating: {name} ({target_status})")
            client.create_contract(contract)

    print(f"Contracts synced to Ontos ({env_name})")


def main():
    parser = argparse.ArgumentParser(description="Sync ODCS contracts to Ontos")
    parser.add_argument("--env", required=True, choices=["dev", "qa", "prod"], help="Target environment")
    args = parser.parse_args()
    sync_contracts(args.env)


if __name__ == "__main__":
    main()
