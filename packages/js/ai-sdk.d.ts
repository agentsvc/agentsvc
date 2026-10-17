import type { Tool } from 'ai';
import type { AgentsvcClient, ServicePick } from './index';
/** AI SDK tools for the picked agentsvc services, keyed by tool name (slug with underscores). */
export function agentsvcTools(client: AgentsvcClient, pick?: ServicePick): Promise<Record<string, Tool>>;
