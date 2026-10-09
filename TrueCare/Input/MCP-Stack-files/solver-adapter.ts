/**
 * Neutral scheduling domain. Both Timefold and the self-hosted solver map
 * to/from these types, so tools and Claude never see vendor payloads.
 * NO PHI: ids, coordinates, windows, skills, weights only.
 */
export interface SolverWorker {
  id: string;                       // DSP id
  homeLocation: { lat: number; lng: number };
  skills: string[];                 // certifications / service codes
  availability: { start: string; end: string }[]; // ISO
  maxMinutes?: number;              // period cap incl. overtime rules
  preferredClientIds?: string[];    // continuity of care
  excludedClientIds?: string[];
}

export interface SolverVisit {
  id: string;                       // shift/visit id
  clientId: string;
  location: { lat: number; lng: number };
  durationMinutes: number;
  timeWindows: { start: string; end: string }[];
  requiredSkills: string[];
  priority?: number;                // 1 (low) .. 5 (critical)
  pinnedWorkerId?: string;          // already confirmed, do not move
  authorizationId?: string;         // for hours-cap constraints
}

export interface SolverObjectives {
  continuityOfCare?: number;
  travelTime?: number;
  overtime?: number;
  fairness?: number;
}

export interface SolverRequest {
  providerId: string;
  rangeStart: string;
  rangeEnd: string;
  workers: SolverWorker[];
  visits: SolverVisit[];
  objectives: SolverObjectives;
}

export interface SolverAssignment {
  visitId: string;
  workerId: string;
  start: string;
  end: string;
  travelMinutes?: number;
}

export interface SolverUnassigned {
  visitId: string;
  reason: string;
}

export interface SolverResult {
  jobId?: string;
  assignments: SolverAssignment[];
  unassigned: SolverUnassigned[];
  score?: Record<string, unknown>;
  explanation?: string;             // human-readable constraint summary
}

export interface ReplacementRequest {
  providerId: string;
  visit: SolverVisit;
  candidates: SolverWorker[];
  currentPlan: SolverAssignment[];
}

export interface ReplacementCandidate {
  workerId: string;
  score: number;
  reasons: string[];
}

export interface SolverAdapter {
  readonly name: 'timefold' | 'self_hosted';
  solve(req: SolverRequest): Promise<SolverResult>;
  recommendReplacement(req: ReplacementRequest): Promise<ReplacementCandidate[]>;
}

export const SOLVER_ADAPTER = Symbol('SOLVER_ADAPTER');
