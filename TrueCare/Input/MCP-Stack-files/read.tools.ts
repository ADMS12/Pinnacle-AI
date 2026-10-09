import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { PrismaService } from '../../../prisma/prisma.service'; // TODO(prisma)
import { AiAuditService } from '../../audit/ai-audit.service';
import { ToolContext } from '../../scope/tool-context';

const json = (v: unknown) => ({ content: [{ type: 'text' as const, text: JSON.stringify(v) }] });
const dateRange = { start: z.string().datetime(), end: z.string().datetime() };

/**
 * Read-only tools. Every query is filtered by ctx.providerId.
 * Return minimal fields — Claude gets what it needs to reason, not whole rows.
 */
export function registerReadTools(server: McpServer, ctx: ToolContext, prisma: PrismaService, audit: AiAuditService) {

  server.registerTool('get_open_shifts', {
    title: 'Open (unassigned) shifts',
    description: 'List shifts in a date range that have no DSP assigned, with client, time window and required skills.',
    inputSchema: dateRange,
  }, async (args) => audit.wrap(ctx, 'get_open_shifts', args, async () => {
    const rows = await prisma.shift.findMany({ // TODO(prisma)
      where: { providerId: ctx.providerId, dspId: null, start: { gte: new Date(args.start) }, end: { lte: new Date(args.end) } },
      select: { id: true, clientId: true, start: true, end: true, serviceCode: true, requiredSkills: true },
    });
    return json(rows);
  }));

  server.registerTool('get_dsp_availability', {
    title: 'DSP availability',
    description: 'Availability windows, skills, and hour caps for DSPs in a date range. Optionally filter by skill.',
    inputSchema: { ...dateRange, skill: z.string().optional() },
  }, async (args) => audit.wrap(ctx, 'get_dsp_availability', args, async () => {
    const rows = await prisma.employee.findMany({ // TODO(prisma)
      where: { providerId: ctx.providerId, role: 'DSP', active: true, ...(args.skill && { skills: { has: args.skill } }) },
      select: { id: true, skills: true, availability: true, maxWeeklyHours: true },
    });
    return json(rows);
  }));

  server.registerTool('get_client_authorizations', {
    title: 'Client authorizations',
    description: 'Authorized services, units and remaining balance for a client (or all clients) in the provider.',
    inputSchema: { clientId: z.string().optional() },
  }, async (args) => audit.wrap(ctx, 'get_client_authorizations', args, async () => {
    const rows = await prisma.authorization.findMany({ // TODO(prisma)
      where: { providerId: ctx.providerId, ...(args.clientId && { clientId: args.clientId }), endDate: { gte: new Date() } },
      select: { id: true, clientId: true, serviceCode: true, unitsAuthorized: true, unitsUsed: true, startDate: true, endDate: true },
    });
    return json(rows);
  }));

  server.registerTool('get_evv_status', {
    title: 'EVV / visit status',
    description: 'Visit verification status (checked-in, missed, late, Sandata ACK state) for a date range.',
    inputSchema: dateRange,
  }, async (args) => audit.wrap(ctx, 'get_evv_status', args, async () => {
    const rows = await prisma.visit.findMany({ // TODO(prisma)
      where: { providerId: ctx.providerId, scheduledStart: { gte: new Date(args.start), lte: new Date(args.end) } },
      select: { id: true, shiftId: true, dspId: true, clientId: true, checkInAt: true, checkOutAt: true, status: true, sandataStatus: true },
    });
    return json(rows);
  }));

  server.registerTool('get_schedule_proposal', {
    title: 'Schedule proposal',
    description: 'Fetch a previously generated schedule proposal and its status.',
    inputSchema: { proposalId: z.string() },
  }, async (args) => audit.wrap(ctx, 'get_schedule_proposal', args, async () => {
    const p = await prisma.scheduleProposal.findFirst({ where: { id: args.proposalId, providerId: ctx.providerId } });
    return json(p ?? { error: 'not found' });
  }));
}
