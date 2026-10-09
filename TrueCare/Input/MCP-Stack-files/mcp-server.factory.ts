import { Inject, Injectable } from '@nestjs/common';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { PrismaService } from '../../prisma/prisma.service'; // TODO(prisma)
import { AiAuditService } from '../audit/ai-audit.service';
import { ToolContext } from '../scope/tool-context';
import { SOLVER_ADAPTER, SolverAdapter } from '../solver/solver-adapter';
import { registerReadTools } from './tools/read.tools';
import { registerOptimizerTools } from './tools/optimizer.tools';
import { registerWriteTools } from './tools/write.tools';

/**
 * Builds a fresh McpServer bound to ONE ToolContext. Binding scope at
 * construction time (closure) is the simplest way to guarantee no tool can
 * ever run without a providerId.
 */
@Injectable()
export class McpServerFactory {
  constructor(
    private readonly prisma: PrismaService,
    private readonly audit: AiAuditService,
    @Inject(SOLVER_ADAPTER) private readonly solver: SolverAdapter,
  ) {}

  create(ctx: ToolContext): McpServer {
    const server = new McpServer({ name: 'truecare-ai', version: '0.1.0' });
    registerReadTools(server, ctx, this.prisma, this.audit);
    registerOptimizerTools(server, ctx, this.prisma, this.audit, this.solver);
    if (ctx.roles.some((r) => ['ADMIN', 'SUPERVISOR'].includes(r))) {
      registerWriteTools(server, ctx, this.prisma, this.audit);
    }
    // Future: registerDocumentationTools, registerBillingTools, registerComplianceTools ...
    return server;
  }
}
