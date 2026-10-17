// LangChain.js tools: const tools = await agentsvcLangChainTools(client, ['web-scrape', 'news-search'])
// then createReactAgent({ llm, tools }) or llm.bindTools(tools).
import { DynamicStructuredTool } from '@langchain/core/tools';
import { selectServices, toolName, toolDescription, toolSchema } from './index.mjs';

export async function agentsvcLangChainTools(client, pick) {
  return (await selectServices(client, pick)).map(s => new DynamicStructuredTool({
    name: toolName(s.slug),
    description: toolDescription(s),
    schema: toolSchema(s),
    func: async input => JSON.stringify(await client.call(s.slug, input)),
  }));
}
