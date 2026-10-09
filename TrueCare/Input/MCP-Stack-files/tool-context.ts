/**
 * Everything a tool needs to know about WHO is calling.
 * Built from your existing auth guard/JWT — never from request body or headers
 * the client controls. Frontend-supplied provider IDs are not trusted.
 */
export interface ToolContext {
  providerId: string;
  userId: string;
  roles: string[]; // e.g. ['ADMIN'], ['SUPERVISOR'], ['DSP']
  channel: 'mcp' | 'orchestrator';
}

export function requireRole(ctx: ToolContext, ...allowed: string[]) {
  if (!ctx.roles.some((r) => allowed.includes(r))) {
    throw new Error(`Forbidden: requires one of [${allowed.join(', ')}]`);
  }
}
