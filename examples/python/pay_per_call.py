"""Call one agentsvc.io service and pay for it with x402 (USDC, no account, no API key).

    pip install "x402[httpx,evm]" eth-account
    EVM_PRIVATE_KEY=0x... python pay_per_call.py token-verdict '{"token": "0x4ed4e862860bed51a9570b96d89af5e1b0efefed", "chain": "base"}'

The wallet needs a few cents of USDC on Base, Polygon or Arbitrum. It pays no gas: the client signs an
EIP-3009 authorization and the facilitator settles it. NETWORK picks the chain (default eip155:8453, Base).
"""
import asyncio
import json
import os
import sys

from eth_account import Account
from x402 import x402Client
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm.exact.register import register_exact_evm_client
from x402.mechanisms.evm.signers import EthAccountSigner

BASE = "https://agentsvc.io/api/v1/proxy"


async def main() -> None:
    slug = sys.argv[1] if len(sys.argv) > 1 else "token-verdict"
    body = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {"token": "0x4ed4e862860bed51a9570b96d89af5e1b0efefed", "chain": "base"}
    network = os.environ.get("NETWORK", "eip155:8453")

    client = x402Client()
    register_exact_evm_client(client, EthAccountSigner(Account.from_key(os.environ["EVM_PRIVATE_KEY"])), networks=network)

    async with x402HttpxClient(client, timeout=120) as http:
        r = await http.post(f"{BASE}/{slug}", json=body)
        print(r.status_code)
        print(json.dumps(r.json(), indent=2)[:3000])


asyncio.run(main())
