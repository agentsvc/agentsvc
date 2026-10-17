"""LangChain tools: tools = agentsvc_tools(Agentsvc(credit_token=...), ["web-scrape", "news-search"])"""
from __future__ import annotations

import json
from typing import Any, Callable, Iterable

from langchain_core.tools import StructuredTool

from . import Agentsvc, tool_description, tool_name


def _schema(s: dict) -> dict:
    sch = dict(s.get("input_schema") or {})
    sch["type"] = "object"
    sch.setdefault("properties", {})
    sch["title"] = tool_name(s["slug"])
    return sch


def agentsvc_tools(client: Agentsvc, pick: Iterable[str] | Callable[[dict], bool] | None = None, category: str | None = None) -> list[StructuredTool]:
    tools = []
    for s in client.select(pick, category):
        slug = s["slug"]

        def run(_slug: str = slug, **kwargs: Any) -> str:
            return json.dumps(client.call(_slug, kwargs))

        async def arun(_slug: str = slug, **kwargs: Any) -> str:
            return json.dumps(await client.acall(_slug, kwargs))

        tools.append(StructuredTool.from_function(func=run, coroutine=arun, name=tool_name(slug), description=tool_description(s), args_schema=_schema(s)))
    return tools
