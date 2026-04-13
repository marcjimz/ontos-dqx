"""Ontos REST API client — modeled on ontos/demo/setup_ontos_demo.py:OntosSetup."""

import json
import os
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
