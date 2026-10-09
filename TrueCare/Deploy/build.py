"""Build index.html from template.html + MCP-Stack-files sources + arch.svg.
Run from TrueCare/Deploy:  python build.py
"""
import html, os, re, json
import buildmap

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'Input', 'MCP-Stack-files')

# (filename, module path, one-line description, role class)
FILES = [
    ('ai.module.ts',            'src/ai/ai.module.ts',                      'NestJS module wiring: controller, factory, audit, solver provider, orchestrator', 'core'),
    ('tool-context.ts',         'src/ai/scope/tool-context.ts',             'ToolContext (providerId, userId, roles, channel) + requireRole()', 'core'),
    ('ai-audit.service.ts',     'src/ai/audit/ai-audit.service.ts',         'Wraps every tool call; writes AiToolAudit rows with timing and output hash', 'core'),
    ('mcp-server.factory.ts',   'src/ai/mcp/mcp-server.factory.ts',         'Builds one McpServer per ToolContext; registers write tools only for ADMIN/SUPERVISOR', 'core'),
    ('mcp.controller.ts',       'src/ai/mcp/mcp.controller.ts',             'POST /mcp — Streamable HTTP, stateless, behind the existing JWT guard', 'core'),
    ('read.tools.ts',           'src/ai/mcp/tools/read.tools.ts',           'get_open_shifts, get_dsp_availability, get_client_authorizations, get_evv_status, get_schedule_proposal', 'tool'),
    ('optimizer.tools.ts',      'src/ai/mcp/tools/optimizer.tools.ts',      'optimize_schedule (creates PENDING proposal), recommend_replacement; data → neutral solver types', 'tool'),
    ('write.tools.ts',          'src/ai/mcp/tools/write.tools.ts',          'apply_schedule — the only mutating tool; refuses unless proposal is APPROVED', 'tool'),
    ('solver-adapter.ts',       'src/ai/solver/solver-adapter.ts',          'SolverAdapter interface + neutral, PHI-free domain types (workers, visits, objectives, results)', 'solver'),
    ('timefold.adapter.ts',     'src/ai/solver/timefold.adapter.ts',        'Phase 1 backend: Timefold Field Service Routing REST (submit → poll → fetch)', 'solver'),
    ('self-hosted.adapter.ts',  'src/ai/solver/self-hosted.adapter.ts',     'Phase 2 backend: your own container speaking the neutral contract at /solve and /recommend', 'solver'),
    ('solver.provider.ts',      'src/ai/solver/solver.provider.ts',         'Picks the adapter from SOLVER_BACKEND', 'solver'),
    ('orchestrator.service.ts', 'src/ai/orchestrator/orchestrator.service.ts', 'Claude tool-use loop over the same MCP tools via in-memory transport ("Selena 2.0")', 'core'),
    ('ai.prisma',               'prisma/ai.prisma',                         'New models: ScheduleProposal (status lifecycle) and AiToolAudit', 'data'),
    ('README.md',               'src/ai/README.md',                         'Skeleton overview, layout, install, env, design rules', 'data'),
]

LANG = {'.ts': 'typescript', '.prisma': 'plaintext', '.md': 'markdown'}


def slug(name):
    return 'f-' + re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


cards, blocks = [], []
for fn, path, desc, role in FILES:
    with open(os.path.join(SRC, fn), encoding='utf-8') as f:
        code = f.read().rstrip('\n')
    lines = code.count('\n') + 1
    ext = os.path.splitext(fn)[1]
    lang = LANG.get(ext, 'plaintext')
    todos = len(re.findall(r'TODO', code))
    sid = slug(fn)
    cards.append(
        f'<a class="file" href="#{sid}"><div class="p">{html.escape(path)}</div>'
        f'<div class="d">{html.escape(desc)}</div>'
        f'<span class="role {role}">{role}</span>'
        + (f' <span class="role" style="background:#fffbeb;color:#b45309">{todos} TODO</span>' if todos else '')
        + '</a>'
    )
    todo_line = (f'<div class="todo">⚠ {todos} TODO marker{"s" if todos != 1 else ""} — map to the real schema / SDK before use.</div>' if todos else '')
    blocks.append(
        f'<details class="src" id="{sid}">'
        f'<summary><span class="fn">{html.escape(path)}</span><span class="desc">{html.escape(desc)}</span>'
        f'<span class="lines">{lines} lines</span><button class="cp" type="button">Copy</button></summary>'
        f'{todo_line}'
        f'<pre><code class="language-{lang}">{html.escape(code)}</code></pre>'
        f'</details>'
    )

with open(os.path.join(HERE, 'arch.svg'), encoding='utf-8') as f:
    svg = f.read().strip()
svg_lb = svg.replace('id="arrow"', 'id="arrowLB"').replace('id="arrowG"', 'id="arrowGLB"') \
            .replace('url(#arrow)', 'url(#arrowLB)').replace('url(#arrowG)', 'url(#arrowGLB)')

with open(os.path.join(HERE, 'template.html'), encoding='utf-8') as f:
    tpl = f.read()

out = (tpl.replace('{{ARCH_SVG_LB}}', svg_lb)
          .replace('{{ARCH_SVG}}', svg)
          .replace('{{FILE_CARDS}}', '\n'.join(cards))
          .replace('{{SOURCE_FILES}}', '\n'.join(blocks)))


buttons = ''.join(f'<button type="button" data-step="{i}">{"Step "+str(i) if i else "Step 0"}</button>' for i in range(13))
bm_data = json.dumps([buildmap.STEP_DONE[i] for i in range(13)])
bm_titles = json.dumps([buildmap.STEP_TITLES[i] for i in range(13)])
out = (out.replace('{{BM_CSS}}', buildmap.CSS.strip())
          .replace('{{BM_BUTTONS}}', buttons)
          .replace('{{BM_MAIN}}', buildmap.svg(None, mini=False, with_ids=True))
          .replace('{{BM_DATA}}', bm_data)
          .replace('{{BM_TITLES}}', bm_titles))
for i in range(13):
    out = out.replace('{{BM_STEP_%d}}' % i, buildmap.svg(i, mini=True))

assert '{{' not in out, 'unreplaced placeholder'
with open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(out)
print(f'index.html written: {len(out):,} bytes, {len(FILES)} source files embedded')
