"""CrewAI tools: Agent(tools=agentsvc_crewai_tools(Agentsvc(credit_token=...), ["web-scrape", "token-precheck"]))"""
from __future__ import annotations

import json
from typing import Any, Callable, Iterable

from crewai.tools import BaseTool
from pydantic import ConfigDict, create_model

from . import Agentsvc, tool_description, tool_name

_TYPES = {"string": str, "integer": int, "number": float, "boolean": bool, "array": list, "object": dict}


def _model(s: dict):
    sch = s.get("input_schema") or {}
    req = set(sch.get("required") or [])
    fields = {}
    for k, v in (sch.get("properties") or {}).items():
        t = _TYPES.get(v.get("type") if isinstance(v.get("type"), str) else "", Any)
        fields[k] = (t, ...) if k in req else (t | None, None)
    return create_model(f"{tool_name(s['slug'])}_input", __config__=ConfigDict(extra="allow"), **fields)


def agentsvc_crewai_tools(client: Agentsvc, pick: Iterable[str] | Callable[[dict], bool] | None = None, category: str | None = None) -> list[BaseTool]:
    out = []
    for s in client.select(pick, category):
        slug = s["slug"]

        class _Tool(BaseTool):
            name: str = tool_name(slug)
            description: str = tool_description(s)
            args_schema: type = _model(s)

            def _run(self, _slug: str = slug, **kwargs: Any) -> str:
                return json.dumps(client.call(_slug, {k: v for k, v in kwargs.items() if v is not None}))

        out.append(_Tool())
    return out
