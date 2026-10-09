# EB-5 report on Render (password-gated)

Serves `../EB5-Chau-Duong-Van-Investigative-Report.html` behind HTTP Basic Auth.
No npm dependencies. The password is read from `SITE_PASSWORD` and is never committed
(this repository is public).

## One-time setup in the Render dashboard

1. New → **Web Service** → connect `ADMS12/Pinnacle-AI`.
2. Settings:
   - Root Directory: `TrueCare/EB5/render`
   - Runtime: Node
   - Build Command: *(leave empty)*
   - Start Command: `node server.js`
   - Health Check Path: `/healthz`
   - Plan: Free
3. Environment → add `SITE_PASSWORD` = the agreed password.
4. Deploy. Open the service URL; the browser prompts for a login. Any username works; enter the password.

Every push to `main` that touches the report or this folder redeploys automatically.

## Local test

```
SITE_PASSWORD=test node server.js
curl -i http://localhost:10000/            # 401
curl -i -u x:test http://localhost:10000/  # 200, the report
```
