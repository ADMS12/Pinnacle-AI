"""Build-map SVG generator: the NEW components from the architecture diagram,
with boxes filled according to which build step has been completed.
Imported by build.py.
"""
import html

# id, x, y, w, h, lines(list), kind ('new' | 'later' | 'ext')
BOXES = [
    # --- client layer
    ('portal',        40,  18, 172, 64, ['Web Portal (existing)'], 'host'),
    ('portal-review', 48,  40,  76, 36, ['Review proposed', 'schedule screen'], 'new'),
    ('portal-panel', 130,  40,  76, 36, ['AI Assistant', 'panel'], 'new'),
    ('assistant',    226,  18, 188, 64, ['Claude AI Assistant', '"Selena 2.0" chat surface', 'shared by portal + mobile'], 'new'),
    ('mobile',       428,  18, 172, 64, ['Mobile App (existing)'], 'host'),
    ('mobile-ask',   436,  40, 156, 36, ['"Ask" chat for DSPs', 'my shifts · directions · open shifts'], 'new'),
    # --- API layer container
    ('module',        40,  98, 560, 140, ['AI Orchestrator + MCP Server (new NestJS module)'], 'host'),
    ('scope',         50, 122,  98, 36, ['Provider scope', '+ audit log'], 'new'),
    ('read',         156, 122,  98, 36, ['Read tools', '(5)'], 'new'),
    ('opt',          262, 122,  98, 36, ['Optimizer tools', 'optimize · replace'], 'new'),
    ('write',        368, 122, 114, 36, ['Write tool (gated)', '+ Proposals REST API'], 'new'),
    ('mcp',          490, 122, 100, 36, ['POST /mcp', 'external MCP clients'], 'new'),
    ('orch',          50, 164, 204, 34, ['Orchestrator (Claude loop)', 'POST /ai/chat'], 'new'),
    ('adapter',      262, 164, 220, 34, ['Solver Adapter', 'fixed contract · swappable backend'], 'new'),
    ('notify',       490, 164, 100, 34, ['Push notifications', '+ per-provider flag'], 'new'),
    ('future',        50, 204, 204, 30, ['Future tools (Phase 3)', 'notes · claims · compliance · KPI'], 'later'),
    ('eval',         262, 204, 328, 30, ['Eval harness · dashboards', 'cost + audit anomaly alerts'], 'new'),
    # --- solver + AI
    ('claude',        40, 252, 172, 44, ['Claude (Anthropic API)', 'under BAA · tool calling'], 'ext'),
    ('timefold',     226, 252, 188, 44, ['Timefold Platform (Phase 1)', 'Field Service Routing API'], 'ext'),
    ('selfhosted',   428, 252, 172, 44, ['Self-hosted solver (Phase 5)', 'OR-Tools / Timefold CE'], 'later'),
    # --- data
    ('db',            40, 312, 560, 42, ['PostgreSQL: + schedule_proposals, ai_tool_audit tables',
                                          '+ lat/lng · skills · availability · requiredSkills · assignedVia on existing rows'], 'new'),
]

BANDS = [(8, 'CLIENT'), (90, 'API'), (244, 'SOLVER + AI'), (304, 'DATA')]

# Which boxes each step completes (cumulative order matters for the "done" state).
STEP_DONE = {
    0: [],
    1: ['db'],
    2: ['module', 'scope'],
    3: ['read'],
    4: ['mcp'],
    5: ['adapter', 'timefold'],
    6: ['opt'],
    7: ['write'],
    8: ['portal', 'portal-review'],
    9: ['orch', 'claude'],
    10: ['assistant', 'portal-panel', 'mobile', 'mobile-ask'],
    11: ['notify'],
    12: ['eval'],
}
STEP_TITLES = {
    0: 'Accounts, keys, branch — nothing built yet',
    1: 'Schema: new tables and fields on existing rows',
    2: 'Module scaffold: provider scope and audit wrapper',
    3: 'Read tools against the real schema',
    4: 'POST /mcp — first live questions via Claude Desktop',
    5: 'Solver adapter mapped to Timefold for real',
    6: 'Optimizer tools; proposals in shadow mode',
    7: 'Write tool + Proposals REST API — the approval gate',
    8: 'Portal review screen — live mode possible',
    9: 'Orchestrator + POST /ai/chat',
    10: 'Chat surfaces: portal panel and mobile Ask',
    11: 'Notifications and per-provider feature flag',
    12: 'Evaluation, monitoring, cost — Phase 4 ready',
}


def cumulative(step):
    done = []
    for s in range(0, step + 1):
        done += STEP_DONE[s]
    return set(done)


def svg(step=None, mini=False, with_ids=False):
    """step=None -> all pending (interactive base). mini -> compact static copy."""
    done = cumulative(step) if step is not None else set()
    now = set(STEP_DONE[step]) if step is not None else set()
    fs_h, fs = (10.5, 9.5) if not mini else (11, 10)
    out = [f'<svg viewBox="0 0 640 364" class="bmap{" mini" if mini else ""}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Build map">']
    for y, lbl in BANDS:
        out.append(f'<text x="4" y="{y+6}" class="band">{lbl}</text>')
        if y > 8:
            out.append(f'<line x1="4" y1="{y-4}" x2="636" y2="{y-4}" class="bandln"/>')
    for bid, x, y, w, h, lines, kind in BOXES:
        cls = ['bx', 'k-'+kind]
        if bid in now: cls.append('now')
        elif bid in done: cls.append('done')
        idattr = f' data-box="{bid}"' if with_ids else ''
        out.append(f'<g class="{" ".join(cls)}"{idattr}>')
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5"/>')
        n = len(lines)
        if kind == 'host':
            ty = y + 13
            out.append(f'<text x="{x+w/2}" y="{ty}" text-anchor="middle" class="th">{html.escape(lines[0])}</text>')
        else:
            lh = fs + 2.5
            ty0 = y + h/2 - (n-1)*lh/2 + fs/2 - 1
            for i, ln in enumerate(lines):
                c = 'th' if i == 0 else 'ts'
                out.append(f'<text x="{x+w/2}" y="{ty0 + i*lh:.1f}" text-anchor="middle" class="{c}">{html.escape(ln)}</text>')
        out.append('</g>')
    out.append('</svg>')
    return '\n'.join(out)


CSS = """
  .bmap{width:100%;height:auto;display:block;font-family:Inter,system-ui,sans-serif}
  .bmap .band{font-size:8.5px;font-weight:700;letter-spacing:.1em;fill:#9ca3af}
  .bmap .bandln{stroke:#e5e7eb;stroke-dasharray:3 3}
  .bmap .bx rect{fill:#fff;stroke:#cbd5e1;stroke-width:1.2}
  .bmap .bx text.th{font-size:10.5px;font-weight:600;fill:#9ca3af}
  .bmap .bx text.ts{font-size:9px;fill:#b0b7c3}
  .bmap .bx.k-host rect{fill:#f8fafc;stroke:#cbd5e1;stroke-dasharray:4 3}
  .bmap .bx.k-host text.th{fill:#94a3b8;font-size:10px}
  .bmap .bx.k-later rect{fill:#fffbeb;stroke:#d97706;stroke-dasharray:5 3}
  .bmap .bx.k-later text.th,.bmap .bx.k-later text.ts{fill:#b45309}
  .bmap .bx.done rect{fill:#ecfdf5;stroke:#0f766e;stroke-width:1.6}
  .bmap .bx.done text.th{fill:#0f766e}.bmap .bx.done text.ts{fill:#0f766e}
  .bmap .bx.done.k-host rect{fill:#f0fdf9;stroke:#0f766e;stroke-dasharray:4 3}
  .bmap .bx.done.k-host text.th{fill:#0f766e}
  .bmap .bx.done.k-ext rect{fill:#f5f3ff;stroke:#6d28d9}
  .bmap .bx.done.k-ext text.th,.bmap .bx.done.k-ext text.ts{fill:#6d28d9}
  .bmap .bx.now rect{fill:#0f766e;stroke:#0f766e;stroke-width:1.6}
  .bmap .bx.now text.th,.bmap .bx.now text.ts{fill:#fff}
  .bmap .bx.now.k-host rect{fill:#ccfbf1;stroke:#0f766e;stroke-dasharray:4 3}
  .bmap .bx.now.k-host text.th{fill:#0f766e}
  .bmap .bx.now.k-ext rect{fill:#6d28d9;stroke:#6d28d9}
  .bmap.mini .bx text.th{font-size:11.5px}.bmap.mini .bx text.ts{font-size:10px}
  .bmap.mini .band{font-size:9.5px}
"""
