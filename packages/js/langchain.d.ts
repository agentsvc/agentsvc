import type { DynamicStructuredTool } from '@langchain/core/tools';
import type { AgentsvcClient, ServicePick } from './index';
/** LangChain.js tools for the picked agentsvc services. */
export function agentsvcLangChainTools(client: AgentsvcClient, pick?: ServicePick): Promise<DynamicStructuredTool[]>;
