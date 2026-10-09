# True Care System — AI Orchestrator + MCP Server (skeleton)

Drop-in NestJS module (`src/ai`) that adds:

1. **MCP Server** (`/mcp` endpoint, Streamable HTTP) exposing provider-scoped tools
   over your existing Prisma models.
2. **Solver Adapter** interface with a Timefold Field Service Routing implementation
   (Phase 1) and a self-hosted stub (Phase 2). The tool contract never changes.
3. **AI Orchestrator** — a Claude tool-calling loop that the portal/mobile chat
   surface calls. Claude only ever sees what MCP tools return.
4. **Audit + approval** — every tool call is logged; `apply_schedule` only runs
   against a proposal a supervisor approved in the portal.

## Layout
```
src/ai/
  ai.module.ts                    NestJS module wiring
  scope/tool-context.ts           ToolContext (providerId, userId, roles) from your auth
  mcp/mcp-server.factory.ts       Builds an McpServer bound to one ToolContext
  mcp/mcp.controller.ts           POST /mcp (Streamable HTTP, stateless)
  mcp/tools/read.tools.ts         get_open_shifts, get_dsp_availability, ...
  mcp/tools/optimizer.tools.ts    optimize_schedule, recommend_replacement
  mcp/tools/write.tools.ts        apply_schedule (approval-gated)
  solver/solver-adapter.ts        SolverAdapter interface + neutral domain types
  solver/timefold.adapter.ts      Phase 1: Timefold FSR REST API
  solver/self-hosted.adapter.ts   Phase 2: OR-Tools / Timefold CE container (stub)
  solver/solver.provider.ts       Picks adapter from SOLVER_BACKEND env
  audit/ai-audit.service.ts       Writes ai_tool_audit rows
  orchestrator/orchestrator.service.ts  Claude Messages API loop
prisma/ai.prisma                  New models: ScheduleProposal, AiToolAudit
```

## Install
```bash
npm i @modelcontextprotocol/sdk zod @anthropic-ai/sdk
```
Env:
```
ANTHROPIC_API_KEY=...
SOLVER_BACKEND=timefold          # or self_hosted
TIMEFOLD_API_KEY=...
TIMEFOLD_BASE_URL=https://app.timefold.ai/api/models/field-service-routing/v1
SELF_HOSTED_SOLVER_URL=http://solver:8080
```

## Design rules baked in
- Provider scope comes from the authenticated user (your existing guard), never from the client.
- Solver payloads carry IDs, coordinates, time windows and skill tags only — no names/PHI.
- Writes are two-step: `optimize_schedule` -> proposal row (PENDING) -> supervisor approves
  in portal -> `apply_schedule(proposal_id)` commits.
- `TODO(prisma)` markers show where to map to your real model/field names.

## Verify before use
The MCP TypeScript SDK and Anthropic SDK APIs move quickly; the import paths and
`registerTool` / `StreamableHTTPServerTransport` signatures below match SDK 1.x and
should be checked against the version you install.
