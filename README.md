<p align="center"><img src="logo.png" width="96" alt="agentsvc.io logo"></p>

# agentsvc.io

**126 pay-per-call APIs for AI agents.** Your agent pays each call in USDC over [x402](https://x402.org), from its own wallet, on Base, Solana, Polygon or Arbitrum. No account, no API key, no subscription. Most calls cost 0.002 to 0.04 USDC, a few multi-source reports up to 0.60 USDC.

Use it as a **remote MCP server** (`https://agentsvc.io/mcp`) or as plain **HTTP endpoints** (`POST https://agentsvc.io/api/v1/proxy/<service>`).

What agents use it for:

- **Memory and messaging for agents:** `agent-memory` is a key-value store that survives between runs and can be shared with other agents (counters, logs, compare-and-set), `agent-inbox` gives your agent an address other agents can send results to, with long polling or a signed webhook. No account: a secret is the key.
- **Finding the right API:** `service-finder` searches the whole x402 market (about 45,000 endpoints, not only ours) for a task in plain words and returns the best matches with price, networks and whether they answered our own check.
- **Following smart money:** `token-smart-money` shows which large wallets are accumulating or dumping a token, whether the first buyers still hold, and how much of the volume is bots.
- **Before a swap:** `token-precheck` answers ALLOW, CAUTION or BLOCK for up to 5 tokens (honeypot simulation, taxes, owner powers, liquidity). `token-verdict` grades one token A to F.
- **Before acting on untrusted text:** `prompt-injection-check` for web pages, tool results and emails, `scam-message-check` for DMs, casts and emails.
- **Before installing a dependency:** `package-check` answers ALLOW, CAUTION or BLOCK for up to 20 packages (npm, PyPI, crates.io, Go, Maven, NuGet, RubyGems): hallucinated names that do not exist, known malware, typosquats, vulnerable versions with a safe upgrade.
- **Before citing a source:** `citation-check` verifies up to 10 references against Crossref and OpenAlex and flags invented, miscited and retracted papers.
- **Reading the web:** `web-scrape` and `site-crawl` to Markdown, `screenshot`, `html-to-pdf`, `answer-with-sources`, `news-search`.
- **Documents and companies:** `invoice-extract`, `pdf-extract`, `ocr`, `company-brief` (LEI, VAT, sanctions, imprint), `sanctions-screen`.
- **Proofs and monitoring:** `iota-notarize` and `btc-timestamp` for tamper-evident hashes, `page-watch`, `token-watch` and `wallet-watch` with webhooks.

The full list with prices is in [SERVICES.md](SERVICES.md), generated from the live catalog.

## Try it free

Every service runs its example input for free, so an agent can see the output shape before paying:

```bash
curl https://agentsvc.io/api/v1/try/token-verdict
```

## MCP

Remote server, streamable HTTP, no install:

```json
{
  "mcpServers": {
    "agentsvc": { "url": "https://agentsvc.io/mcp" }
  }
}
```

Claude Code: `claude mcp add --transport http agentsvc https://agentsvc.io/mcp`

**Claude.ai, ChatGPT and other OAuth connectors:** add `https://agentsvc.io/mcp/credit` as a custom connector. The client signs in with OAuth; you paste a credit token from https://agentsvc.io/credits once, and every tool call is paid from that credit.

Tools called with their example input are free. For paid calls the client attaches an x402 payment in `_meta["x402/payment"]` of `tools/call`; x402-aware MCP clients such as `@x402/mcp` do this automatically. If your client cannot pay, run the local bridge, which pays from a wallet you give it:

```json
{
  "mcpServers": {
    "agentsvc": {
      "command": "node",
      "args": ["/path/to/mcp-server.mjs"],
      "env": { "EVM_PRIVATE_KEY": "0x..." }
    }
  }
}
```

Download it from https://agentsvc.io/mcp-server.mjs and install its dependencies once: `npm i @x402/fetch @x402/evm viem`. Use a separate wallet that holds only a few dollars of USDC.

## HTTP with x402

A call without payment returns `402 Payment Required` with the price. The x402 client signs an EIP-3009 authorization, retries, and gets the result. The wallet pays no gas.

TypeScript ([examples/typescript](examples/typescript/pay-per-call.mjs)):

```js
import { wrapFetchWithPayment, x402Client } from '@x402/fetch';
import { registerExactEvmScheme } from '@x402/evm/exact/client';
import { privateKeyToAccount } from 'viem/accounts';

const client = new x402Client();
registerExactEvmScheme(client, { signer: privateKeyToAccount(process.env.EVM_PRIVATE_KEY) });
const payFetch = wrapFetchWithPayment(fetch, client);

const res = await payFetch('https://agentsvc.io/api/v1/proxy/token-precheck', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ tokens: ['0x4ed4e862860bed51a9570b96d89af5e1b0efefed'], chain: 'base' }),
});
console.log(await res.json());
```

Python ([examples/python](examples/python/pay_per_call.py)):

```python
from eth_account import Account
from x402 import x402Client
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm.exact.register import register_exact_evm_client
from x402.mechanisms.evm.signers import EthAccountSigner

client = x402Client()
register_exact_evm_client(client, EthAccountSigner(Account.from_key(KEY)))
async with x402HttpxClient(client) as http:
    r = await http.post("https://agentsvc.io/api/v1/proxy/scam-message-check",
                        json={"text": "Your wallet is compromised, verify your seed phrase at ...", "channel": "email"})
```

Both examples were run against the live service with a real USDC payment on Polygon.

## A2A

Agent2Agent (0.3) server at `https://agentsvc.io/a2a` (JSON-RPC) and `https://agentsvc.io/a2a/v1/message:send` (HTTP+JSON), with the [x402 extension for A2A](https://github.com/google-agentic-commerce/a2a-x402): send a data part `{"service": "<slug>", "input": {...}}`, the task comes back as `input-required` with `x402.payment.required`, answer with the same `taskId` and `x402.payment.payload`. Runnable client: [agentsvc/a2a-x402-payment-example](https://github.com/agentsvc/a2a-x402-payment-example).

## Packages

| | Install | Adapters |
|---|---|---|
| JavaScript | `npm i agentsvc` ([packages/js](packages/js)) | Vercel AI SDK (`agentsvc/ai-sdk`), LangChain.js (`agentsvc/langchain`) |
| Python | `pip install agentsvc` ([packages/python](packages/python)) | LangChain (`agentsvc.langchain`), CrewAI (`agentsvc.crewai`) |

Both pay with a credit token or from a wallet via x402 and turn any selection of services into framework tools with the live input schemas.

## Examples

- [x402-token-check-before-swap](https://github.com/agentsvc/x402-token-check-before-swap): a trading agent asks ALLOW, CAUTION or BLOCK and who is buying before it swaps (TypeScript).
- [a2a-x402-payment-example](https://github.com/agentsvc/a2a-x402-payment-example): pay an A2A agent with x402 (TypeScript).
- [agent-inbox-handoff-example](https://github.com/agentsvc/agent-inbox-handoff-example): two agents hand work to each other through an inbox and shared memory (Python).

## OpenAI-compatible paths

Same x402 payment and prices, OpenAI request and response format, base URL `https://agentsvc.io/v1`:

| Path | Service | Price |
|---|---|---|
| `POST /v1/embeddings` | text-embed (all-MiniLM-L6-v2) | 0.002 USDC |
| `POST /v1/rerank` (Cohere/Jina format) | text-embed | 0.002 USDC |
| `POST /v1/audio/speech` | tts (returns audio bytes) | 0.04 USDC |
| `POST /v1/audio/transcriptions` (multipart, `whisper-1`) | audio-transcribe | 0.01 USDC |

The OpenAI SDK has no x402 support, so either give it a fetch that pays x402 (for example `@x402/fetch`), or use a prepaid credit token (see below) as `api_key`. `GET /v1/models` lists the paths.

## Whole tasks in one call

`POST https://agentsvc.io/api/v1/proxy/agent-run` with `{"task": "..."}` (0.50 USDC): a Claude Haiku 5.5 agent uses up to 38 of the tools above and returns a Markdown answer with sources and the list of tool calls. Read only, up to 12 steps.

## No wallet?

Buy a prepaid credit token at https://agentsvc.io/credits and send it as `Authorization: Bearer asvc_cr_...`. Each call is deducted from the balance.

## Machine-readable

| What | Where |
|---|---|
| Catalog with input and output schemas | https://agentsvc.io/api/v1/services |
| OpenAPI 3.1 | https://agentsvc.io/openapi.json |
| x402 discovery | https://agentsvc.io/.well-known/x402 |
| Guide for agents | https://agentsvc.io/llms.txt and https://agentsvc.io/llms-full.txt |
| MCP server card | https://agentsvc.io/.well-known/mcp.json |
| A2A agent card | https://agentsvc.io/.well-known/agent-card.json |
| OAuth metadata (MCP connectors) | https://agentsvc.io/.well-known/oauth-protected-resource/mcp/credit |
| DID | `did:web:agentsvc.io` |

Listed in the Coinbase CDP Bazaar, on x402scan and in the official MCP registry as `io.agentsvc/services`. Registered on Base under ERC-8004 as agent #98109.

## Plugins

- Coinbase AgentKit action provider: [coinbase/agentkit#1552](https://github.com/coinbase/agentkit/pull/1552)
- GOAT SDK plugin: [goat-sdk/goat#604](https://github.com/goat-sdk/goat/pull/604)

## About this repository

This repository holds documentation, examples and the logo. The service itself runs at agentsvc.io and is not open source. Questions and bug reports: open an issue or write to agents@agentsvc.io.

The examples are MIT licensed.
