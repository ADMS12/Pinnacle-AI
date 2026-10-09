// Vercel Edge Middleware: HTTP Basic Auth gate for the whole site.
// Password comes from the SITE_PASSWORD environment variable (set in the Vercel project),
// so no secret lives in this file. Any username is accepted.
export const config = { matcher: '/(.*)' };

export default function middleware(request) {
  const expected = (process.env.SITE_PASSWORD || "").trim();
  if (!expected) {
    return new Response('Site password not configured', { status: 500 });
  }
  const auth = request.headers.get('authorization') || '';
  if (auth.startsWith('Basic ')) {
    try {
      const decoded = atob(auth.slice(6));
      const idx = decoded.indexOf(':');
      const pass = idx >= 0 ? decoded.slice(idx + 1) : decoded;
      if (pass === expected) return; // continue to the static file
    } catch (e) { /* fall through */ }
  }
  return new Response('Authentication required', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="Pearl Hospice analysis", charset="UTF-8"',
      'Cache-Control': 'no-store',
    },
  });
}
