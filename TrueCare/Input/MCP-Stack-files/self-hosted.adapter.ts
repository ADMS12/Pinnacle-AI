import { Injectable } from '@nestjs/common';
import {
  SolverAdapter, SolverRequest, SolverResult, ReplacementRequest, ReplacementCandidate,
} from './solver-adapter';

/**
 * Phase 2 backend: your own container (OR-Tools/Python or Timefold CE/Java)
 * exposing POST /solve and POST /recommend that speak the neutral types directly.
 * Because the container speaks SolverRequest/SolverResult, this adapter is trivial.
 */
@Injectable()
export class SelfHostedAdapter implements SolverAdapter {
  readonly name = 'self_hosted' as const;
  private readonly base = process.env.SELF_HOSTED_SOLVER_URL ?? 'http://solver:8080';

  async solve(req: SolverRequest): Promise<SolverResult> {
    return this.post('/solve', req);
  }

  async recommendReplacement(req: ReplacementRequest): Promise<ReplacementCandidate[]> {
    return this.post('/recommend', req);
  }

  private async post(path: string, body: unknown) {
    const res = await fetch(this.base + path, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`Solver ${path} -> ${res.status}`);
    return res.json();
  }
}
