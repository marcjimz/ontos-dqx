#!/usr/bin/env python3
"""Deploy DDL and seed data to a target Databricks environment."""

import argparse
import sys
from pathlib import Path

# Allow imports from scripts/lib
sys.path.insert(0, str(Path(__file__).parent))

from lib.config import load_environment
from lib.databricks_sql import get_client, execute_sql


def deploy(env_name: str, seed: bool = False):
    env = load_environment(env_name)
    client = get_client()
    wh = env["warehouse_id"]
    catalog = env["catalog"]
    schema = env["schema"]

    print(f"Deploying to {catalog}.{schema} ({env_name})")

    # 1. Ensure catalog and schema exist
    print(f"  Creating catalog: {catalog}")
    execute_sql(client, wh, f"CREATE CATALOG IF NOT EXISTS {catalog}")
    print(f"  Creating schema: {catalog}.{schema}")
    execute_sql(client, wh, f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")

    # 2. Apply DDLs in order
    ddl_dir = Path(__file__).parent.parent / "sql" / "ddl"
    for ddl_file in sorted(ddl_dir.glob("*.sql")):
        print(f"  Applying DDL: {ddl_file.name}")
        sql = ddl_file.read_text()
        execute_sql(client, wh, sql, catalog=catalog)

    # 3. Apply seed data (truncate first to avoid duplicates)
    if seed:
        tables = ["members", "formulary", "claims"]
        for t in tables:
            execute_sql(client, wh, f"TRUNCATE TABLE {catalog}.{schema}.{t}")
        seed_dir = Path(__file__).parent.parent / "sql" / "seed"
        for seed_file in sorted(seed_dir.glob("*.sql")):
            print(f"  Seeding: {seed_file.name}")
            sql = seed_file.read_text()
            execute_sql(client, wh, sql, catalog=catalog)

    print(f"Deployment complete: {catalog}.{schema}")


def main():
    parser = argparse.ArgumentParser(description="Deploy DDL and seed data to Databricks")
    parser.add_argument("--env", required=True, choices=["dev", "qa", "prod"], help="Target environment")
    parser.add_argument("--seed", action="store_true", help="Also load seed data")
    args = parser.parse_args()
    deploy(args.env, seed=args.seed)


if __name__ == "__main__":
    main()
