// Tiny zero-dependency server: serves static files + /api/lead -> Telegram
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 80;
const TG_TOKEN = '8814710536:AAFewXSFvDKcaP2YtVK8K64cy8zPYnAdCYc';
const TG_CHAT = '5041739228';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg':  'image/svg+xml',
  '.ico':  'image/x-icon',
  '.css':  'text/css; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.txt':  'text/plain; charset=utf-8'
};

function sendToTelegram(text) {
  return new Promise((resolve) => {
    const body = JSON.stringify({
      chat_id: TG_CHAT,
      text: text,
      parse_mode: 'Markdown'
    });
    const req = https.request({
      hostname: 'api.telegram.org',
      port: 443,
      path: '/bot' + TG_TOKEN + '/sendMessage',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      },
      timeout: 10000
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { resolve({ ok: false, raw: data }); }
      });
    });
    req.on('error', (err) => resolve({ ok: false, error: err.message }));
    req.on('timeout', () => { req.destroy(); resolve({ ok: false, error: 'timeout' }); });
    req.write(body);
    req.end();
  });
}

function formatLead(payload) {
  const lines = [
    '🎓 *Новая заявка с сайта*',
    '',
    '👤 *Имя:* ' + (payload.name || '—'),
    '📞 *Телефон:* ' + (payload.phone || '—'),
    '🏫 *Класс:* ' + (payload.grade || '—'),
    '📍 *Город:* ' + (payload.city || '—'),
    '📚 *Направление:* ' + (payload.direction || '—')
  ];
  if (payload.goal) lines.push('💬 *Цель:* ' + payload.goal);
  lines.push('');
  lines.push('🕐 ' + new Date().toLocaleString('ru-RU', { timeZone: 'Europe/Moscow' }) + ' (МСК)');
  return lines.join('\n');
}

function readBody(req, limit = 100 * 1024) {
  return new Promise((resolve, reject) => {
    let total = 0;
    const chunks = [];
    req.on('data', (chunk) => {
      total += chunk.length;
      if (total > limit) {
        req.destroy();
        return reject(new Error('payload too large'));
      }
      chunks.push(chunk);
    });
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}

function parsePayload(raw, contentType) {
  if (!raw) return {};
  if ((contentType || '').includes('application/json')) {
    try { return JSON.parse(raw); } catch { return {}; }
  }
  const out = {};
  for (const pair of raw.split('&')) {
    if (!pair) continue;
    const eq = pair.indexOf('=');
    const k = decodeURIComponent((eq >= 0 ? pair.slice(0, eq) : pair).replace(/\+/g, ' '));
    const v = eq >= 0 ? decodeURIComponent(pair.slice(eq + 1).replace(/\+/g, ' ')) : '';
    out[k] = v;
  }
  return out;
}

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function serveStatic(req, res) {
  let urlPath = req.url.split('?')[0];
  if (urlPath === '/') urlPath = '/index.html';
  const filePath = path.join(__dirname, urlPath.replace(/\.\./g, ''));
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, {
      'Content-Type': MIME[ext] || 'application/octet-stream',
      'Cache-Control': ext === '.html' ? 'no-cache' : 'public, max-age=3600'
    });
    res.end(data);
  });
}

const server = http.createServer(async (req, res) => {
  const url = req.url.split('?')[0];

  // CORS preflight
  if (req.method === 'OPTIONS') {
    setCors(res);
    res.writeHead(204);
    res.end();
    return;
  }

  // Lead endpoint
  if (url === '/api/lead' && (req.method === 'POST' || req.method === 'GET')) {
    setCors(res);
    try {
      let payload;
      if (req.method === 'GET') {
        const qs = req.url.indexOf('?') >= 0 ? req.url.slice(req.url.indexOf('?') + 1) : '';
        payload = parsePayload(qs, 'application/x-www-form-urlencoded');
      } else {
        const body = await readBody(req);
        payload = parsePayload(body, req.headers['content-type']);
      }
      const result = await sendToTelegram(formatLead(payload));
      res.writeHead(result.ok ? 200 : 502, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify(result));
      console.log(new Date().toISOString(), 'lead:', payload.name || '?', payload.phone || '?', '->', result.ok ? 'OK' : 'FAIL');
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify({ ok: false, error: err.message }));
      console.error('lead error:', err);
    }
    return;
  }

  // Health
  if (url === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('ok');
    return;
  }

  // Static files
  serveStatic(req, res);
});

server.listen(PORT, () => {
  console.log('Server listening on port', PORT);
});
