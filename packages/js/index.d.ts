export interface AgentsvcOptions { privateKey?: string; network?: string; payFetch?: typeof fetch; creditToken?: string; baseUrl?: string }
export interface Service { slug: string; name: string; description: string; category: string; price_usdc: number; input_schema: Record<string, unknown>; output_schema?: Record<string, unknown>; example_input?: Record<string, unknown>; is_active?: boolean; tags: string[] }
export interface AgentsvcClient {
  call<T = unknown>(slug: string, input?: Record<string, unknown>): Promise<T>;
  sample<T = unknown>(slug: string): Promise<T>;
  services(): Promise<Service[]>;
  baseUrl: string;
}
export class AgentsvcError extends Error { status?: number; body?: unknown }
export function createAgentsvc(opts?: AgentsvcOptions): AgentsvcClient;
export type ServicePick = string[] | { category: string } | ((s: Service) => boolean);
export function selectServices(client: AgentsvcClient, pick?: ServicePick): Promise<Service[]>;
export function toolName(slug: string): string;
export function toolDescription(s: Service): string;
export function toolSchema(s: Service): Record<string, unknown>;
