"""Load environment configuration from environments.yaml + env vars."""

import os
from pathlib import Path
from typing import Dict, Any

import yaml


def load_environment(env_name: str) -> Dict[str, Any]:
    """Load environment config, merging YAML definitions with env vars.

    Args:
        env_name: One of 'dev', 'qa', 'prod'

    Returns:
        Dict with keys: catalog, schema, contract_status,
        databricks_host, databricks_token, warehouse_id, ontos_base_url
    """
    config_path = Path(__file__).parent.parent.parent / "config" / "environments.yaml"
    with open(config_path) as f:
        all_envs = yaml.safe_load(f)

    if env_name not in all_envs["environments"]:
        raise ValueError(f"Unknown environment: {env_name}. Must be one of: {list(all_envs['environments'].keys())}")

    env = all_envs["environments"][env_name]

    # Merge in env vars (required)
    env["databricks_host"] = os.environ.get("DATABRICKS_HOST", "")
    env["databricks_token"] = os.environ.get("DATABRICKS_TOKEN", "")
    env["warehouse_id"] = os.environ.get("DATABRICKS_WAREHOUSE_ID", "")
    env["ontos_base_url"] = os.environ.get("ONTOS_BASE_URL", "")
    env["databricks_profile"] = os.environ.get("DATABRICKS_PROFILE")
    env["ontos_oauth_token"] = os.environ.get("ONTOS_OAUTH_TOKEN", "")

    return env
