import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { PrismaService } from '../../../prisma/prisma.service'; // TODO(prisma)
import { AiAuditService } from '../../audit/ai-audit.service';
import { ToolContext, requireRole } from '../../scope/tool-context';
import { SolverAdapter, SolverRequest, SolverVisit, SolverWorker } from '../../solver/solver-adapter';

const json = (v: unknown) => ({ content: [{ type: 'text' as const, text: JSON.stringify(v) }] });

/**
 * Optimizer tools. These NEVER write to shifts — they create a ScheduleProposal
 * (PENDING) that a supervisor approves in the portal before apply_schedule runs.
 */
export function registerOptimizerTools(server: McpServer, ctx: ToolContext, prisma: PrismaService, audit: AiAuditService, solver: SolverAdapter) {

  server.registerTool('optimize_schedule', {
    title: 'Optimize schedule (creates a proposal)',
    description: 'Run the scheduling optimizer for a date range. Returns a proposal id, assignments, unassigned visits and an explanation. Does not change live schedules.',
    inputSchema: {
      start: z.string().datetime(),
      end: z.string().datetime(),
      objectives: z.object({
        continuityOfCare: z.number().min(0).max(10).default(5),
        travelTime: z.number().min(0).max(10).default(5),
        overtime: z.number().min(0).max(10).default(7),
        fairness: z.number().min(0).max(10).default(3),
      }).default({}),
      onlyOpenShifts: z.boolean().default(true),
    },
  }, async (args) => audit.wrap(ctx, 'optimize_schedule', args, async () => {
    requireRole(ctx, 'ADMIN', 'SCHEDULER', 'SUPERVISOR');
    const req = await buildSolverRequest(prisma, ctx.providerId, args.start, args.end, args.onlyOpenShifts, args.objectives);
    const result = await solver.solve(req);
    const proposal = await prisma.scheduleProposal.create({
      data: {
        providerId: ctx.providerId, requestedById: ctx.userId,
        rangeStart: new Date(args.start), rangeEnd: new Date(args.end),
        objectives: args.objectives, solverBackend: solver.name, solverJobId: result.jobId,
        assignments: result.assignments as any, unassigned: result.unassigned as any,
        score: result.score as any, explanation: result.explanation,
      },
    });
    return json({
      proposalId: proposal.id, status: proposal.status,
      assigned: result.assignments.length, unassigned: result.unassigned,
      explanation: result.explanation,
      nextStep: 'A supervisor must approve this proposal in the portal before it is applied.',
    });
  }));

  server.registerTool('recommend_replacement', {
    title: 'Recommend replacement DSP',
    description: 'For a shift whose DSP called out, rank qualified, available DSPs with reasons (skills, distance, overtime, continuity).',
    inputSchema: { shiftId: z.string(), limit: z.number().int().min(1).max(10).default(5) },
  }, async (args) => audit.wrap(ctx, 'recommend_replacement', args, async () => {
    const shift = await prisma.shift.findFirst({ where: { id: args.shiftId, providerId: ctx.providerId }, include: { client: true } }); // TODO(prisma)
    if (!shift) return json({ error: 'shift not found' });
    const visit = toVisit(shift);
    const dayStart = new Date(shift.start); dayStart.setHours(0, 0, 0, 0);
    const dayEnd = new Date(dayStart); dayEnd.setDate(dayEnd.getDate() + 1);
    const { workers, currentPlan } = await loadWorkersAndPlan(prisma, ctx.providerId, dayStart, dayEnd);
    const ranked = await solver.recommendReplacement({ providerId: ctx.providerId, visit, candidates: workers, currentPlan });
    return json(ranked.slice(0, args.limit));
  }));
}

// ---- data -> neutral solver types (IDs/coords/windows only, no PHI) -------

async function buildSolverRequest(prisma: PrismaService, providerId: string, start: string, end: string, onlyOpen: boolean, objectives: any): Promise<SolverRequest> {
  const shifts = await prisma.shift.findMany({ // TODO(prisma)
    where: { providerId, start: { gte: new Date(start) }, end: { lte: new Date(end) }, ...(onlyOpen && { dspId: null }) },
    include: { client: { select: { id: true, lat: true, lng: true } } },
  });
  const { workers } = await loadWorkersAndPlan(prisma, providerId, new Date(start), new Date(end));
  return { providerId, rangeStart: start, rangeEnd: end, workers, visits: shifts.map(toVisit), objectives };
}

async function loadWorkersAndPlan(prisma: PrismaService, providerId: string, start: Date, end: Date) {
  const dsps = await prisma.employee.findMany({ // TODO(prisma)
    where: { providerId, role: 'DSP', active: true },
    include: { assignedShifts: { where: { start: { gte: start }, end: { lte: end } } } },
  });
  const workers: SolverWorker[] = dsps.map((d: any) => ({
    id: d.id, homeLocation: { lat: d.lat, lng: d.lng }, skills: d.skills ?? [],
    availability: d.availability ?? [], maxMinutes: (d.maxWeeklyHours ?? 40) * 60,
    preferredClientIds: d.preferredClientIds ?? [], excludedClientIds: d.excludedClientIds ?? [],
  }));
  const currentPlan = dsps.flatMap((d: any) => d.assignedShifts.map((s: any) => ({
    visitId: s.id, workerId: d.id, start: s.start.toISOString(), end: s.end.toISOString(),
  })));
  return { workers, currentPlan };
}

function toVisit(s: any): SolverVisit {
  return {
    id: s.id, clientId: s.clientId,
    location: { lat: s.client?.lat ?? s.lat, lng: s.client?.lng ?? s.lng },
    durationMinutes: Math.round((new Date(s.end).getTime() - new Date(s.start).getTime()) / 60000),
    timeWindows: [{ start: new Date(s.windowStart ?? s.start).toISOString(), end: new Date(s.windowEnd ?? s.end).toISOString() }],
    requiredSkills: s.requiredSkills ?? [],
    priority: s.priority ?? 3,
    pinnedWorkerId: s.dspId ?? undefined,
    authorizationId: s.authorizationId ?? undefined,
  };
}
