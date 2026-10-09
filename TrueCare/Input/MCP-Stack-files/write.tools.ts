import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { PrismaService } from '../../../prisma/prisma.service'; // TODO(prisma)
import { AiAuditService } from '../../audit/ai-audit.service';
import { ToolContext, requireRole } from '../../scope/tool-context';

const json = (v: unknown) => ({ content: [{ type: 'text' as const, text: JSON.stringify(v) }] });

/**
 * The only tool that mutates live schedules. It refuses unless the proposal
 * was APPROVED by a supervisor/admin via the portal (approval happens in your
 * existing REST API, not through Claude).
 */
export function registerWriteTools(server: McpServer, ctx: ToolContext, prisma: PrismaService, audit: AiAuditService) {

  server.registerTool('apply_schedule', {
    title: 'Apply an approved schedule proposal',
    description: 'Commit assignments from an APPROVED proposal to live shifts. Fails if the proposal is not approved.',
    inputSchema: { proposalId: z.string() },
  }, async (args) => audit.wrap(ctx, 'apply_schedule', args, async () => {
    requireRole(ctx, 'ADMIN', 'SUPERVISOR');
    const p = await prisma.scheduleProposal.findFirst({ where: { id: args.proposalId, providerId: ctx.providerId } });
    if (!p) return json({ error: 'proposal not found' });
    if (p.status !== 'APPROVED') return json({ error: `proposal is ${p.status}; approve it in the portal first` });

    const assignments = p.assignments as { visitId: string; workerId: string }[];
    try {
      await prisma.$transaction(async (tx) => {
        for (const a of assignments) {
          await tx.shift.updateMany({ // TODO(prisma): also re-validate authorization balance here
            where: { id: a.visitId, providerId: ctx.providerId, dspId: null },
            data: { dspId: a.workerId, assignedVia: 'AI_PROPOSAL', proposalId: p.id },
          });
        }
        await tx.scheduleProposal.update({ where: { id: p.id }, data: { status: 'APPLIED', appliedAt: new Date() } });
      });
      return json({ applied: assignments.length, proposalId: p.id });
    } catch (e: any) {
      await prisma.scheduleProposal.update({ where: { id: p.id }, data: { status: 'FAILED' } });
      throw e;
    }
  }));
}
