// Vercel AI SDK tools: const tools = await agentsvcTools(client, ['web-scrape', 'token-precheck'])
// then generateText({ model, tools, prompt, stopWhen: stepCountIs(5) }).
import { tool, jsonSchema } from 'ai';
import { selectServices, toolName, toolDescription, toolSchema } from './index.mjs';

export async function agentsvcTools(client, pick) {
  const out = {};
  for (const s of await selectServices(client, pick)) {
    const def = { description: toolDescription(s), execute: input => client.call(s.slug, input) };
    // AI SDK 5 heisst das Feld inputSchema, AI SDK 4 parameters
    def.inputSchema = jsonSchema(toolSchema(s));
    def.parameters = def.inputSchema;
    out[toolName(s.slug)] = tool(def);
  }
  return out;
}
