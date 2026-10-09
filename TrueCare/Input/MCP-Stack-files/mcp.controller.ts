import { Controller, Post, Req, Res, UseGuards } from '@nestjs/common';
import type { Request, Response } from 'express';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { JwtAuthGuard } from '../../auth/jwt-auth.guard'; // TODO: your existing guard
import { McpServerFactory } from './mcp-server.factory';
import { ToolContext } from '../scope/tool-context';

/**
 * POST /mcp — Streamable HTTP transport, stateless (one server per request).
 * Used by external MCP clients (claude.ai connectors, Claude Desktop, Claude Code)
 * with a bearer token from your auth system. The in-app chat uses the
 * Orchestrator instead, which calls the same tools in-process.
 */
@Controller('mcp')
@UseGuards(JwtAuthGuard)
export class McpController {
  constructor(private readonly factory: McpServerFactory) {}

  @Post()
  async handle(@Req() req: Request, @Res() res: Response) {
    const user = (req as any).user; // populated by JwtAuthGuard
    const ctx: ToolContext = { providerId: user.providerId, userId: user.id, roles: user.roles, channel: 'mcp' };

    const server = this.factory.create(ctx);
    const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
    res.on('close', () => { transport.close(); server.close(); });
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  }
}
