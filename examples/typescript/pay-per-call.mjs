// Call one agentsvc.io service and pay for it with x402 (USDC, no account, no API key).
//
//   npm i @x402/fetch @x402/evm viem
//   EVM_PRIVATE_KEY=0x... node pay-per-call.mjs token-precheck '{"tokens":["0x4ed4e862860bed51a9570b96d89af5e1b0efefed"],"chain":"base"}'
//
// The wallet needs a few cents of USDC on Base, Polygon or Arbitrum and pays no gas: the client signs an
// EIP-3009 authorization and the facilitator settles it. NETWORK picks the chain (default eip155:8453, Base).
import { wrapFetchWithPayment, x402Client } from '@x402/fetch';
import { registerExactEvmScheme } from '@x402/evm/exact/client';
import { privateKeyToAccount } from 'viem/accounts';

const slug = process.argv[2] || 'token-precheck';
const body = process.argv[3] ? JSON.parse(process.argv[3]) : { tokens: ['0x4ed4e862860bed51a9570b96d89af5e1b0efefed'], chain: 'base' };
const network = process.env.NETWORK || 'eip155:8453';
const maxUsdc = Number(process.env.MAX_USDC || '0.05');

// Pick the offer for our chain and refuse anything above the cap
const client = new x402Client((_version, accepts) => {
  const offer = accepts.find((a) => a.network === network);
  if (!offer) throw new Error(`${network} not offered: ${accepts.map((a) => a.network).join(', ')}`);
  if (Number(offer.amount ?? offer.maxAmountRequired) / 1e6 > maxUsdc) throw new Error(`price above ${maxUsdc} USDC`);
  return offer;
});
registerExactEvmScheme(client, { signer: privateKeyToAccount(process.env.EVM_PRIVATE_KEY) });
const payFetch = wrapFetchWithPayment(fetch, client);

const res = await payFetch(`https://agentsvc.io/api/v1/proxy/${slug}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
});
console.log(res.status);
console.log(JSON.stringify(await res.json(), null, 2).slice(0, 3000));
