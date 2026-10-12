# Installing the agentsvc.io MCP server

agentsvc.io is a remote MCP server. Nothing needs to be installed or built.

1. Add this entry to the MCP settings (for Cline: `cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "agentsvc": {
      "url": "https://agentsvc.io/mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

2. No API key is needed. Every tool works for free with its example input, which is enough to verify the connection: call `token_verdict` with no arguments changed from its example.

3. Paid calls need an x402 payment in USDC. If the user wants paid calls and the client cannot attach x402 payments itself, use the local bridge instead: download https://agentsvc.io/mcp-server.mjs, run `npm i @x402/fetch @x402/evm viem` in its folder, and configure `"command": "node", "args": ["<path>/mcp-server.mjs"], "env": {"EVM_PRIVATE_KEY": "<key of a wallet with a few dollars of USDC on Base>"}`. Ask the user for the key; never invent or generate one, and suggest a separate low-balance wallet.

Alternatively the user can buy a prepaid credit token at https://agentsvc.io/credits and send it as the header `Authorization: Bearer asvc_cr_...`.
