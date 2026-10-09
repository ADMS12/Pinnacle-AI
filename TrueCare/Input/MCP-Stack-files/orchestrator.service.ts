import { Injectable } from '@nestjs/common';
import Anthropic from '@anthropic-ai/sdk';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { InMemoryTransport } from '@modelcontextprotocol/sdk/inMemory.js';
import { McpServerFactory } from '../mcp/mcp-server.factory';
import { ToolContext } from '../scope/tool-context';

export interface ChatTurn { role: 'user' | 'assistant'; content: string }

/**
 * In-app AI assistant ("Selena 2.0"). Portal and mobile POST the conversation
 * here; we run a Claude tool-use loop against the SAME MCP tools, in-process,
 * via an in-memory transport. Claude sees tool results only — never the DB.
 */
@Injectable()
export class OrchestratorService {
  private readonly anthropic = new Anthropic();
  private readonly model = process.env.CLAUDE_MODEL ?? 'claude-sonnet-4-6'; // verify current model id

  constructor(private readonly factory: McpServerFactory) {}

  async chat(ctx: ToolContext, history: ChatTurn[]): Promise<string> {
    const server = this.factory.create({ ...ctx, channel: 'orchestrator' });
    const [clientT, serverT] = InMemoryTransport.createLinkedPair();
    await server.connect(serverT);
    const client = new Client({ name: 'truecare-orchestrator', version: '0.1.0' });
    await client.connect(clientT);

    try {
      const { tools } = await client.listTools();
      const anthropicTools = tools.map((t) => ({ name: t.name, description: t.description ?? '', input_schema: t.inputSchema as any }));
      const messages: Anthropic.MessageParam[] = history.map((h) => ({ role: h.role, content: h.content }));

      for (let i = 0; i < 8; i++) { // hard cap on tool-call rounds
        const resp = await this.anthropic.messages.create({
          model: this.model, max_tokens: 2000, system: this.systemPrompt(ctx), tools: anthropicTools, messages,
        });
        messages.push({ role: 'assistant', content: resp.content });
        if (resp.stop_reason !== 'tool_use') {
          return resp.content.filter((b) => b.type === 'text').map((b: any) => b.text).join('\n');
        }
        const results: Anthropic.ToolResultBlockParam[] = [];
        for (const block of resp.content) {
          if (block.type !== 'tool_use') continue;
          const r = await client.callTool({ name: block.name, arguments: block.input as any });
          results.push({ type: 'tool_result', tool_use_id: block.id, content: (r.content as any[]).map((c) => c.text ?? '').join('\n') });
        }
        messages.push({ role: 'user', content: results });
      }
      return 'I could not finish that request within the allowed number of steps.';
    } finally {
      await client.close(); await server.close();
    }
  }

  private systemPrompt(ctx: ToolContext) {
    return [
      'You are the True Care System assistant for a home care / I/DD provider.',
      `The user has roles: ${ctx.roles.join(', ')}. Only use the tools available to you.`,
      'Scheduling changes are proposals; tell the user a supervisor must approve them in the portal.',
      'Be concise. Cite the specific shift/client/DSP ids you relied on. Never guess data you did not retrieve.',
    ].join(' ');
  }
}
