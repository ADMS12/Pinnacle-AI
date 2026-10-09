# TrueCare AI proposal — deploy folder

Password-protected review site for the AI Scheduling & Assistant (MCP) proposal.

| File | Purpose |
|---|---|
| `template.html` | Authored page with `{{ARCH_SVG}}`, `{{FILE_CARDS}}`, `{{SOURCE_FILES}}` placeholders |
| `build.py` | Injects `../Input/MCP-Stack-files/*`, `arch.svg` and the build map into `index.html` |
| `buildmap.py` | Generates the "new components" build-map SVGs; edit `BOXES` / `STEP_DONE` here to change what each step fills in |
| `index.html` | Generated output (do not edit by hand) |
| `ai-scheduling.html` | Implementation review page, served at `/ai-scheduling`. Copy of `../Output/True-Care-AI-Scheduling-v2.html` (V1 with internal review observations stays local); rebuild from `../Input/TC-AI-VN/` |
| `arch.svg` | Architecture diagram with C2PA metadata stripped |
| `truecare-ai-mcp-skeleton.zip` | Copy of the skeleton zip, served as a download |
| `middleware.js` | Basic Auth gate; password read from `SITE_PASSWORD` env var |
| `vercel.json` | Clean URLs, no-index, no-store headers |

## Rebuild and deploy

```
cd TrueCare/Deploy
python build.py
vercel deploy --prod --yes
```

The Vercel project is `truecare-ai-proposal` (org `durendal-s-projects`). The password is stored only as
the `SITE_PASSWORD` environment variable on the project. To change it:

```
vercel env rm SITE_PASSWORD production --yes
vercel env add SITE_PASSWORD production   # paste new value
vercel deploy --prod --yes                # redeploy so the edge picks it up
```

After every deploy, verify: a request without auth returns 401, with the password returns 200.
