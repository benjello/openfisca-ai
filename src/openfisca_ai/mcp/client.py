"""HTTP client for OpenFisca Web API."""

import os
from typing import Any

import httpx

from .errors import ConnectionError, format_api_error


class OpenFiscaClient:
    """Client for interacting with OpenFisca Web API."""

    def __init__(self, base_url: str | None = None, timeout: float = 30.0):
        """Initialize OpenFisca API client."""
        self.base_url = base_url or os.getenv("OPENFISCA_API_URL", "http://localhost:5000")
        self.timeout = timeout
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)
        return self._client

    def close(self):
        if self._client is not None:
            self._client.close()
            self._client = None

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        if response.status_code >= 400:
            try:
                data = response.json()
            except Exception:
                data = {"error": response.text}
            raise format_api_error(data, response.status_code)
        return response.json()

    def _get(self, path: str) -> dict[str, Any]:
        try:
            return self._handle_response(self.client.get(path))
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Cannot connect to OpenFisca API at {self.base_url}",
                details={"url": self.base_url, "error": str(e)},
            )

    def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        try:
            return self._handle_response(self.client.post(path, json=data))
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Cannot connect to OpenFisca API at {self.base_url}",
                details={"url": self.base_url, "error": str(e)},
            )

    def get_entities(self) -> dict[str, Any]:
        return self._get("/entities")

    def get_variables(self) -> dict[str, Any]:
        return self._get("/variables")

    def get_variable(self, variable_id: str) -> dict[str, Any]:
        return self._get(f"/variable/{variable_id}")

    def get_parameters(self) -> dict[str, Any]:
        return self._get("/parameters")

    def get_parameter(self, parameter_id: str) -> dict[str, Any]:
        return self._get(f"/parameter/{parameter_id}")

    def calculate(self, situation: dict[str, Any]) -> dict[str, Any]:
        return self._post("/calculate", situation)

    def trace(self, situation: dict[str, Any]) -> dict[str, Any]:
        return self._post("/trace", situation)
