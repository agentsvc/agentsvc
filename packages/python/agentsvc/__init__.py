"""Client for https://agentsvc.io: every service is one HTTP endpoint, paid per call.

Pay with a prepaid credit token from https://agentsvc.io/credits (credit_token=..., or env AGENTSVC_CREDIT_TOKEN),
or with x402 from a wallet (private_key=..., needs `pip install agentsvc[wallet]`).
Without either, only the free samples work (each service's example input).
"""
from __future__ import annotations

import os
from typing import Any, Callable, Iterable

import httpx

__all__ = ["Agentsvc", "AgentsvcError", "tool_name", "tool_description"]
__version__ = "0.1.0"
DEFAULT_BASE = "https://agentsvc.io"


class AgentsvcError(Exception):
    def __init__(self, message: str, status: int | None = None, body: Any = None):
        super().__init__(message)
        self.status, self.body = status, body


def tool_name(slug: str) -> str:
    return slug.replace("-", "_")


def tool_description(s: dict) -> str:
    return f"{s['description']} Costs ${s['price_usdc']} per call."


class Agentsvc:
    def __init__(self, credit_token: str | None = None, private_key: str | None = None, network: str | None = None,
                 base_url: str = DEFAULT_BASE, timeout: float = 120):
        self.base = base_url.rstrip("/")
        self.credit = credit_token or os.environ.get("AGENTSVC_CREDIT_TOKEN")
        self.private_key, self.network, self.timeout = private_key, network, timeout
        self._catalog: list[dict] | None = None
        self._x402 = None

    # ---- Katalog
    def services(self) -> list[dict]:
        if self._catalog is None:
            r = httpx.get(f"{self.base}/api/v1/services", timeout=30)
            r.raise_for_status()
            j = r.json()
            self._catalog = [s for s in (j.get("data") or j.get("services") or []) if s.get("is_active", True)]
        return self._catalog

    def select(self, pick: Iterable[str] | Callable[[dict], bool] | None = None, category: str | None = None) -> list[dict]:
        all_ = self.services()
        if category:
            return [s for s in all_ if s["category"] == category]
        if pick is None:
            return all_
        if callable(pick):
            return [s for s in all_ if pick(s)]
        wanted = list(pick)
        found = [s for s in all_ if s["slug"] in wanted]
        missing = set(wanted) - {s["slug"] for s in found}
        if missing:
            raise AgentsvcError(f"unknown services: {', '.join(sorted(missing))}")
        return found

    # ---- Aufrufe
    def _headers(self) -> dict:
        h = {"Content-Type": "application/json", "User-Agent": f"agentsvc-python/{__version__}"}
        if self.credit:
            h["Authorization"] = f"Bearer {self.credit}"
        return h

    @staticmethod
    def _result(r: httpx.Response, slug: str) -> Any:
        try:
            j = r.json()
        except ValueError:
            j = {}
        if r.status_code == 402:
            raise AgentsvcError(j.get("hint") or f"Payment required for {slug}: pass credit_token or private_key", 402, j)
        if r.status_code >= 400 or j.get("success") is False:
            raise AgentsvcError(j.get("message") or j.get("error") or f"HTTP {r.status_code}", r.status_code, j)
        return j.get("data", j)

    def call(self, slug: str, input: dict | None = None) -> Any:
        """Call one service. Errors (402, invalid input, service error) raise AgentsvcError and are never charged."""
        if self.private_key and not self.credit:
            import asyncio
            return asyncio.run(self.acall(slug, input))
        url = f"{self.base}/api/v1/proxy/{slug}" if self.credit else f"{self.base}/api/v1/try/{slug}"
        r = httpx.post(url, json=input or {}, headers=self._headers(), timeout=self.timeout)
        return self._result(r, slug)

    async def acall(self, slug: str, input: dict | None = None) -> Any:
        if self.credit or not self.private_key:
            async with httpx.AsyncClient(timeout=self.timeout) as http:
                url = f"{self.base}/api/v1/proxy/{slug}" if self.credit else f"{self.base}/api/v1/try/{slug}"
                return self._result(await http.post(url, json=input or {}, headers=self._headers()), slug)
        try:
            from eth_account import Account
            from x402 import x402Client
            from x402.http.clients import x402HttpxClient
            from x402.mechanisms.evm.exact.register import register_exact_evm_client
            from x402.mechanisms.evm.signers import EthAccountSigner
        except ImportError as e:  # pragma: no cover
            raise AgentsvcError("Paying from a wallet needs: pip install 'agentsvc[wallet]'") from e
        if self._x402 is None:
            net = self.network
            client = x402Client(payment_requirements_selector=(lambda _v, accepts: next((a for a in accepts if a.network == net), accepts[0])) if net else None)
            register_exact_evm_client(client, EthAccountSigner(Account.from_key(self.private_key)))
            self._x402 = client
        async with x402HttpxClient(self._x402, timeout=self.timeout) as http:
            r = await http.post(f"{self.base}/api/v1/proxy/{slug}", json=input or {}, headers=self._headers())
            return self._result(r, slug)

    def sample(self, slug: str) -> Any:
        """Free sample with the service's example input."""
        return self._result(httpx.get(f"{self.base}/api/v1/try/{slug}", timeout=self.timeout), slug)
