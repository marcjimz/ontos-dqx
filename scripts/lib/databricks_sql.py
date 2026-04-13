"""Databricks SQL execution via SDK — modeled on ontos/demo/lib/databricks_client.py."""

import os
import time
from typing import Any, Optional

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState


def get_client() -> WorkspaceClient:
    """Initialize Databricks SDK client from environment variables."""
    host = os.environ.get("DATABRICKS_HOST", "")
    token = os.environ.get("DATABRICKS_TOKEN")
    profile = os.environ.get("DATABRICKS_PROFILE")

    if profile:
        return WorkspaceClient(profile=profile)
    return WorkspaceClient(host=host, token=token)


def execute_sql(
    client: WorkspaceClient,
    warehouse_id: str,
    sql: str,
    catalog: Optional[str] = None,
    wait_timeout: str = "50s",
) -> Any:
    """Execute SQL with optional ${CATALOG} variable substitution.

    Args:
        client: Databricks WorkspaceClient
        warehouse_id: SQL Warehouse ID
        sql: SQL statement (may contain ${CATALOG} placeholder)
        catalog: Catalog name to substitute for ${CATALOG}
        wait_timeout: Initial wait timeout

    Returns:
        Query result object

    Raises:
        RuntimeError: If SQL execution fails
    """
    if catalog:
        sql = sql.replace("${CATALOG}", catalog)

    response = client.statement_execution.execute_statement(
        warehouse_id=warehouse_id,
        statement=sql,
        wait_timeout=wait_timeout,
    )

    while response.status.state in [StatementState.PENDING, StatementState.RUNNING]:
        time.sleep(2)
        response = client.statement_execution.get_statement(response.statement_id)

    if response.status.state == StatementState.SUCCEEDED:
        return response.result
    elif response.status.state == StatementState.CANCELED:
        raise RuntimeError(f"SQL was canceled\nSQL: {sql}")
    else:
        error_msg = response.status.error.message if response.status.error else "Unknown error"
        raise RuntimeError(f"SQL failed: {error_msg}\nSQL: {sql}")
