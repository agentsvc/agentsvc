# agentsvc (Python)

Pay-per-call tools for AI agents from [agentsvc.io](https://agentsvc.io): 120+ web, data and crypto APIs (web scraping to Markdown, token safety checks, smart-money tracking, agent memory and inbox, PDF and OCR, company data, and more), paid per call in USDC via [x402](https://x402.org). No account, no subscription.

```bash
pip install agentsvc                 # client, pay with a credit token
pip install "agentsvc[langchain]"    # + LangChain tools
pip install "agentsvc[crewai]"       # + CrewAI tools
pip install "agentsvc[wallet]"       # + pay from your own wallet with x402
```

## Pay

- **Credit token:** buy one at https://agentsvc.io/credits (from $0.10, +10% bonus), then `Agentsvc(credit_token="asvc_cr_...")` or set `AGENTSVC_CREDIT_TOKEN`.
- **Wallet:** `Agentsvc(private_key="0x...", network="eip155:8453")` with a few dollars of USDC on Base, Polygon or Arbitrum. Use a separate low-balance wallet.
- Neither: `client.sample("web-scrape")` runs the free example of any service.

```python
from agentsvc import Agentsvc

svc = Agentsvc(credit_token="asvc_cr_...")
page = svc.call("web-scrape", {"url": "https://example.com"})
check = svc.call("token-precheck", {"tokens": ["0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed"], "chain": "base"})
```

## LangChain

```python
from agentsvc import Agentsvc
from agentsvc.langchain import agentsvc_tools
from langgraph.prebuilt import create_react_agent

tools = agentsvc_tools(Agentsvc(credit_token="asvc_cr_..."), ["web-scrape", "news-search", "agent-memory"])
agent = create_react_agent("anthropic:claude-haiku-5-5", tools)
```

## CrewAI

```python
from agentsvc import Agentsvc
from agentsvc.crewai import agentsvc_crewai_tools
from crewai import Agent

researcher = Agent(role="Researcher", goal="...", backstory="...",
                   tools=agentsvc_crewai_tools(Agentsvc(credit_token="asvc_cr_..."), ["search-read", "answer-with-sources"]))
```

Pick services by slug list, `category="finance"`, or a filter function. The full list with prices: https://agentsvc.io/api/v1/services. Failed calls are never charged.

MIT licensed. The service itself runs at agentsvc.io and is not open source.
