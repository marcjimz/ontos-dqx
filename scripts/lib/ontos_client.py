"""Ontos REST API client — modeled on ontos/demo/setup_ontos_demo.py:OntosSetup."""

import json
import subprocess
import time
from typing import Any, Dict, List, Optional

import requests


class OntosClient:
    """Thin wrapper around the Ontos REST API for contract and DQX operations."""

    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        databricks_profile: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        elif databricks_profile:
            result = subprocess.run(
                ["databricks", "auth", "token", "--profile", databricks_profile],
                capture_output=True,
                text=True,
                check=True,
            )
            access_token = json.loads(result.stdout)["access_token"]
            self.session.headers["Authorization"] = f"Bearer {access_token}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        resp = self.session.request(method, f"{self.base_url}{path}", **kwargs)
        resp.raise_for_status()
        return resp

    # --- Contract CRUD ---

    def list_contracts(self) -> List[Dict]:
        return self._request("GET", "/api/data-contracts").json()

    def create_contract(self, contract_data: Dict) -> Dict:
        return self._request("POST", "/api/data-contracts", json=contract_data).json()

    def update_contract(self, contract_id: str, updates: Dict) -> Dict:
        return self._request("PUT", f"/api/data-contracts/{contract_id}", json=updates).json()

    def get_contract(self, contract_id: str) -> Dict:
        return self._request("GET", f"/api/data-contracts/{contract_id}").json()

    def upload_contract(self, contract_yaml: str) -> Dict:
        return self._request("POST", "/api/data-contracts/upload", json={"yaml_content": contract_yaml}).json()

    # --- DQX Profiling ---

    def start_profiling(self, contract_id: str, schema_names: List[str]) -> Dict:
        return self._request(
            "POST",
            f"/api/data-contracts/{contract_id}/profile",
            json={"schema_names": schema_names},
        ).json()

    def get_profile_runs(self, contract_id: str) -> List[Dict]:
        return self._request("GET", f"/api/data-contracts/{contract_id}/profile-runs").json()

    def get_suggestions(self, contract_id: str, run_id: str) -> List[Dict]:
        return self._request(
            "GET",
            f"/api/data-contracts/{contract_id}/profile-runs/{run_id}/suggestions",
        ).json()

    def accept_suggestions(self, contract_id: str, suggestion_ids: List[str]) -> Dict:
        return self._request(
            "POST",
            f"/api/data-contracts/{contract_id}/suggestions/accept",
            json={"suggestion_ids": suggestion_ids},
        ).json()

    # --- Workflow Jobs ---

    def start_workflow(self, workflow_id: str) -> Dict:
        return self._request("POST", f"/api/jobs/workflows/{workflow_id}/start").json()

    def get_job_status(self, run_id: int) -> Dict:
        return self._request("GET", f"/api/jobs/{run_id}/status").json()

    # --- Polling helpers ---

    def wait_for_profiling(
        self, contract_id: str, timeout: int = 600, poll_interval: int = 10
    ) -> Dict:
        """Poll profile-runs until the latest run completes or fails."""
        start = time.time()
        while time.time() - start < timeout:
            runs = self.get_profile_runs(contract_id)
            if runs and runs[0].get("status") in ("completed", "failed"):
                return runs[0]
            time.sleep(poll_interval)
        raise TimeoutError(f"Profiling did not complete within {timeout}s")

    def wait_for_job(
        self, run_id: int, timeout: int = 600, poll_interval: int = 15
    ) -> Dict:
        """Poll job status until terminal state."""
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_job_status(run_id)
            state = status.get("state", {}).get("life_cycle_state", "")
            if state in ("TERMINATED", "SKIPPED", "INTERNAL_ERROR"):
                return status
            time.sleep(poll_interval)
        raise TimeoutError(f"Job {run_id} did not complete within {timeout}s")
