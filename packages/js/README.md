# agentsvc (JavaScript)

Pay-per-call tools for AI agents from [agentsvc.io](https://agentsvc.io): 120+ web, data and crypto APIs (web scraping to Markdown, token safety checks, smart-money tracking, agent memory and inbox, PDF and OCR, company data, and more), paid per call in USDC via [x402](https://x402.org). No account, no subscription. Ready-made tools for the **Vercel AI SDK** and **LangChain.js**.

```bash
npm i agentsvc
npm i @x402/fetch @x402/evm viem   # only if your agent pays from its own wallet
```

## Pay

- **Credit token:** buy one at https://agentsvc.io/credits (from $0.10, +10% bonus), then `createAgentsvc({ creditToken: 'asvc_cr_...' })` or set `AGENTSVC_CREDIT_TOKEN`.
- **Wallet:** `createAgentsvc({ privateKey: '0x...', network: 'eip155:8453' })` with a few dollars of USDC on Base, Polygon (`eip155:137`) or Arbitrum (`eip155:42161`). Use a separate low-balance wallet.
- **Your own x402 fetch:** `createAgentsvc({ payFetch })`.
- Neither: `client.sample('web-scrape')` runs the free example of any service.

```js
import { createAgentsvc } from 'agentsvc';

const svc = createAgentsvc({ creditToken: process.env.AGENTSVC_CREDIT_TOKEN });
const page = await svc.call('web-scrape', { url: 'https://example.com' });
const check = await svc.call('token-precheck', { tokens: ['0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed'], chain: 'base' });
```

## Vercel AI SDK

```js
import { generateText, stepCountIs } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';
import { createAgentsvc } from 'agentsvc';
import { agentsvcTools } from 'agentsvc/ai-sdk';

const tools = await agentsvcTools(createAgentsvc({ creditToken: process.env.AGENTSVC_CREDIT_TOKEN }), ['web-scrape', 'news-search', 'token-smart-money']);
const { text } = await generateText({ model: anthropic('claude-haiku-5-5'), tools, stopWhen: stepCountIs(5), prompt: 'Who is buying BRETT on Base right now?' });
```

## LangChain.js

```js
import { createAgentsvc } from 'agentsvc';
import { agentsvcLangChainTools } from 'agentsvc/langchain';

const tools = await agentsvcLangChainTools(createAgentsvc({ creditToken: process.env.AGENTSVC_CREDIT_TOKEN }), { category: 'web' });
// createReactAgent({ llm, tools }) or llm.bindTools(tools)
```

Pick services by slug list, `{ category: 'finance' }` or a filter function. The full list with prices: https://agentsvc.io/api/v1/services. Failed calls are never charged; errors throw `AgentsvcError` with `status` and `body`.

MIT licensed. The service itself runs at agentsvc.io and is not open source.
