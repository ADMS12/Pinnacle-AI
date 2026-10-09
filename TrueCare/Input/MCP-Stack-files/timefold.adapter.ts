import { Injectable, Logger } from '@nestjs/common';
import {
  SolverAdapter, SolverRequest, SolverResult, ReplacementRequest, ReplacementCandidate,
} from './solver-adapter';

/**
 * Phase 1 backend: Timefold Field Service Routing API.
 * Flow: POST dataset -> poll status -> GET solution. Field names below are
 * illustrative; align them with the FSR OpenAPI spec for your account.
 */
@Injectable()
export class TimefoldAdapter implements SolverAdapter {
  readonly name = 'timefold' as const;
  private readonly log = new Logger(TimefoldAdapter.name);
  private readonly base = process.env.TIMEFOLD_BASE_URL!;
  private readonly key = process.env.TIMEFOLD_API_KEY!;

  async solve(req: SolverRequest): Promise<SolverResult> {
    const payload = this.toTimefold(req);
    const jobId = await this.submit(payload);
    await this.waitUntilDone(jobId, 120_000);
    const solution = await this.get(`/route-plans/${jobId}`);
    return this.fromTimefold(jobId, solution);
  }

  async recommendReplacement(req: ReplacementRequest): Promise<ReplacementCandidate[]> {
    // TODO: call the FSR recommendations endpoint with current plan + orphaned
    // visit and map returned scores. Stubbed with a skills-only filter for now.
    return req.candidates
      .filter((c) => req.visit.requiredSkills.every((s) => c.skills.includes(s)))
      .map((c) => ({ workerId: c.id, score: 0, reasons: ['skills match (stub)'] }));
  }

  // ---- mapping -----------------------------------------------------------
  private toTimefold(req: SolverRequest) {
    return {
      config: { run: { name: `tcs-${req.providerId}-${req.rangeStart}` } },
      vehicles: req.workers.map((w) => ({
        id: w.id,
        startLocation: [w.homeLocation.lat, w.homeLocation.lng],
        skills: w.skills,
        shifts: w.availability.map((a, i) => ({ id: `${w.id}-${i}`, start: a.start, end: a.end })),
      })),
      visits: req.visits.map((v) => ({
        id: v.id,
        location: [v.location.lat, v.location.lng],
        serviceDuration: `PT${v.durationMinutes}M`,
        timeWindows: v.timeWindows,
        requiredSkills: v.requiredSkills,
        priority: v.priority,
        pinnedVehicleId: v.pinnedWorkerId,
        group: v.clientId, // "prefer same vehicle for group" models continuity of care
      })),
      // TODO: translate req.objectives into FSR constraint weights
    };
  }

  private fromTimefold(jobId: string, sol: any): SolverResult {
    const assignments = (sol.vehicles ?? []).flatMap((veh: any) =>
      (veh.itinerary ?? []).map((it: any) => ({
        visitId: it.id, workerId: veh.id, start: it.arrivalTime, end: it.departureTime,
        travelMinutes: it.travelTimeFromPreviousMinutes,
      })),
    );
    const unassigned = (sol.unassignedVisits ?? []).map((u: any) => ({
      visitId: u.id, reason: u.reason ?? 'no feasible assignment',
    }));
    return { jobId, assignments, unassigned, score: sol.score, explanation: sol.scoreExplanation };
  }

  // ---- http --------------------------------------------------------------
  private async submit(body: unknown): Promise<string> {
    const r = await this.post('/route-plans', body);
    return r.id;
  }

  private async waitUntilDone(jobId: string, timeoutMs: number) {
    const t0 = Date.now();
    while (Date.now() - t0 < timeoutMs) {
      const s = await this.get(`/route-plans/${jobId}/status`);
      if (['SOLVING_COMPLETED', 'TERMINATED'].includes(s.solverStatus)) return;
      if (s.solverStatus === 'FAILED') throw new Error(`Timefold job ${jobId} failed`);
      await new Promise((res) => setTimeout(res, 2000));
    }
    throw new Error(`Timefold job ${jobId} timed out`);
  }

  private async post(path: string, body: unknown) {
    const res = await fetch(this.base + path, {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'X-API-KEY': this.key },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`Timefold ${path} -> ${res.status}`);
    return res.json();
  }

  private async get(path: string) {
    const res = await fetch(this.base + path, { headers: { 'X-API-KEY': this.key } });
    if (!res.ok) throw new Error(`Timefold ${path} -> ${res.status}`);
    return res.json();
  }
}
