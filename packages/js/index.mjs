// agentsvc: client for https://agentsvc.io. Every service is one HTTP endpoint, paid per call:
//  - with x402 from a wallet (pass privateKey, or your own x402-enabled fetch as payFetch), or
//  - with a prepaid credit token from https://agentsvc.io/credits (pass creditToken).
// Without either, only the free samples work (each service's example input).

const DEFAULT_BASE = 'https://agentsvc.io';

export class AgentsvcError extends Error {
  constructor(message, { status, body } = {}) { super(message); this.name = 'AgentsvcError'; this.status = status; this.body = body; }
}

async function walletFetch(privateKey, network) {
  let mods;
  try {
    mods = await Promise.all([import('@x402/fetch'), import('@x402/evm/exact/client'), import('viem/accounts')]);
  } catch {
    throw new AgentsvcError('Paying from a wallet needs the x402 packages: npm i @x402/fetch @x402/evm viem');
  }
  const [{ wrapFetchWithPayment, x402Client }, { registerExactEvmScheme }, { privateKeyToAccount }] = mods;
  const pick = network ? (_v, accepts) => accepts.find(a => a.network === network) || accepts[0] : undefined;
  const client = new x402Client(pick);
  registerExactEvmScheme(client, { signer: privateKeyToAccount(privateKey) });
  return wrapFetchWithPayment(fetch, client);
}

/**
 * @param {object} [opts]
 * @param {string} [opts.privateKey]   EVM key of a wallet with a few dollars of USDC (Base, Polygon or Arbitrum). Use a separate low-balance wallet.
 * @param {string} [opts.network]      Preferred payment network, e.g. "eip155:8453" (Base, default), "eip155:137" (Polygon)
 * @param {Function} [opts.payFetch]   Your own fetch that handles x402 (instead of privateKey)
 * @param {string} [opts.creditToken]  Prepaid credit token (asvc_cr_...) from https://agentsvc.io/credits
 * @param {string} [opts.baseUrl]
 */
export function createAgentsvc(opts = {}) {
  const base = (opts.baseUrl || DEFAULT_BASE).replace(/\/$/, '');
  const credit = opts.creditToken || (typeof process !== 'undefined' ? process.env.AGENTSVC_CREDIT_TOKEN : undefined);
  let fetcher = opts.payFetch || null;
  let catalog = null;

  async function getFetch() {
    if (fetcher) return fetcher;
    if (credit) return (fetcher = fetch);
    if (opts.privateKey) return (fetcher = await walletFetch(opts.privateKey, opts.network));
    return fetch;
  }

  async function services() {
    if (!catalog) {
      const r = await fetch(`${base}/api/v1/services`);
      if (!r.ok) throw new AgentsvcError(`catalog HTTP ${r.status}`, { status: r.status });
      const j = await r.json();
      catalog = j.data || j.services || j;
    }
    return catalog;
  }

  /** Call one service. Returns its data; throws AgentsvcError on 402 (no payment), input errors and service errors (none of them are charged). */
  async function call(slug, input = {}) {
    const f = await getFetch();
    const headers = { 'Content-Type': 'application/json', 'User-Agent': 'agentsvc-js/0.1.1' };
    if (credit) headers.Authorization = `Bearer ${credit}`;
    const paid = credit || opts.privateKey || opts.payFetch;
    const url = paid ? `${base}/api/v1/proxy/${slug}` : `${base}/api/v1/try/${slug}`;
    const r = await f(url, { method: 'POST', headers, body: JSON.stringify(input) });
    const j = await r.json().catch(() => ({}));
    if (r.status === 402) throw new AgentsvcError(j.hint || `Payment required for ${slug}: pass privateKey, payFetch or creditToken`, { status: 402, body: j });
    if (!r.ok || j.success === false) throw new AgentsvcError(j.message || j.error || `HTTP ${r.status}`, { status: r.status, body: j });
    return j.data ?? j;
  }

  /** Free sample of a service with its example input (no payment). */
  async function sample(slug) {
    const r = await fetch(`${base}/api/v1/try/${slug}`);
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new AgentsvcError(j.message || `HTTP ${r.status}`, { status: r.status, body: j });
    return j.data ?? j;
  }

  return { call, sample, services, baseUrl: base };
}

/** Pick catalog entries by slug list, category or a filter function. */
export async function selectServices(client, pick) {
  const all = (await client.services()).filter(s => s.is_active !== false);
  if (!pick) return all;
  if (Array.isArray(pick)) {
    const set = new Set(pick);
    const found = all.filter(s => set.has(s.slug));
    const missing = pick.filter(p => !found.some(s => s.slug === p));
    if (missing.length) throw new AgentsvcError(`unknown services: ${missing.join(', ')}`);
    return found;
  }
  if (typeof pick === 'function') return all.filter(pick);
  if (pick.category) return all.filter(s => s.category === pick.category);
  return all;
}

export const toolName = slug => slug.replace(/-/g, '_');
export const toolDescription = s => `${s.description} Costs $${s.price_usdc} per call.`;
export function toolSchema(s) {
  return { ...(s.input_schema || {}), type: 'object' };
}
