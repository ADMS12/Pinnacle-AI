// Minimal password-gated static server for Render (no dependencies).
// Serves the EB-5 investigative report behind HTTP Basic Auth.
// The password comes from the SITE_PASSWORD environment variable set in the
// Render dashboard, so no secret lives in this public repository.
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 10000;
const REPORT = path.join(__dirname, '..', 'EB5-Chau-Duong-Van-Investigative-Report.html');
const REALM = 'EB-5 investigative report';

function authorized(req) {
  const expected = (process.env.SITE_PASSWORD || '').trim();
  if (!expected) return false;
  const header = req.headers['authorization'] || '';
  if (!header.startsWith('Basic ')) return false;
  try {
    const decoded = Buffer.from(header.slice(6), 'base64').toString('utf8');
    const idx = decoded.indexOf(':');
    const pass = idx >= 0 ? decoded.slice(idx + 1) : decoded;
    return pass === expected;
  } catch (e) {
    return false;
  }
}

const server = http.createServer((req, res) => {
  if (req.url === '/healthz') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    return res.end('ok');
  }
  if (!(process.env.SITE_PASSWORD || '').trim()) {
    res.writeHead(500, { 'Content-Type': 'text/plain' });
    return res.end('Site password not configured (set SITE_PASSWORD).');
  }
  if (!authorized(req)) {
    res.writeHead(401, {
      'WWW-Authenticate': `Basic realm="${REALM}", charset="UTF-8"`,
      'Cache-Control': 'no-store',
      'Content-Type': 'text/plain',
    });
    return res.end('Authentication required');
  }
  fs.readFile(REPORT, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      return res.end('Report not found');
    }
    res.writeHead(200, {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-store',
      'X-Robots-Tag': 'noindex, nofollow',
    });
    res.end(data);
  });
});

server.listen(PORT, () => console.log(`Listening on ${PORT}`));
