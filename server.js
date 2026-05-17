const express = require('express');
const path = require('path');
const https = require('https');

const app = express();
const PORT = process.env.PORT || 3000;
const BOT_TOKEN = process.env.BOT_TOKEN || '8814710536:AAFewXSFvDKcaP2YtVK8K64cy8zPYnAdCYc';
let CHAT_ID = process.env.CHAT_ID || '5041739228';

app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Helper: HTTPS GET returning parsed JSON
function tgGet(method, params = {}) {
  const qs = new URLSearchParams(params).toString();
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/${method}${qs ? '?' + qs : ''}`;
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

// Helper: HTTPS POST returning parsed JSON
function tgPost(method, body) {
  const payload = JSON.stringify(body);
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/${method}`,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) }
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

// Auto-detect CHAT_ID from the most recent message sent to the bot
async function detectChatId() {
  if (CHAT_ID) return CHAT_ID;
  try {
    const upd = await tgGet('getUpdates', { limit: 10 });
    if (upd.ok && upd.result.length > 0) {
      const msg = upd.result[upd.result.length - 1];
      CHAT_ID = (msg.message || msg.channel_post || msg.callback_query?.message)?.chat?.id;
      if (CHAT_ID) console.log('Auto-detected CHAT_ID:', CHAT_ID);
    }
  } catch (e) {
    console.error('getUpdates error:', e.message);
  }
  return CHAT_ID;
}

// /setup — visit once in browser to confirm bot is linked
app.get('/setup', async (req, res) => {
  const id = await detectChatId();
  if (id) {
    await tgPost('sendMessage', { chat_id: id, text: '✅ Сервер подключён! Заявки будут приходить сюда.' });
    res.json({ ok: true, chat_id: id });
  } else {
    res.json({ ok: false, message: 'Нет сообщений. Напишите боту /start, затем обновите эту страницу.' });
  }
});

// Main endpoint: receive lead from form
app.post('/api/lead', async (req, res) => {
  const { name, phone, grade, city, direction, goal } = req.body || {};

  const chatId = await detectChatId();
  if (!chatId) {
    console.error('CHAT_ID not set and could not be detected');
    return res.status(500).json({ ok: false, error: 'chat_id not configured' });
  }

  const lines = [
    '🎓 *Новая заявка с сайта*',
    '',
    `👤 *Имя:* ${name || '—'}`,
    `📞 *Телефон:* ${phone || '—'}`,
    `🏫 *Класс:* ${grade || '—'}`,
    `📍 *Город:* ${city || '—'}`,
    `📚 *Направление:* ${direction || '—'}`,
    goal ? `💬 *Цель:* ${goal}` : null,
    '',
    `🕐 ${new Date().toLocaleString('ru-RU', { timeZone: 'Europe/Moscow' })} (МСК)`
  ].filter(l => l !== null).join('\n');

  try {
    const result = await tgPost('sendMessage', {
      chat_id: chatId,
      text: lines,
      parse_mode: 'Markdown'
    });

    if (result.ok) {
      res.json({ ok: true });
    } else {
      console.error('Telegram error:', result);
      res.status(500).json({ ok: false, error: result.description });
    }
  } catch (e) {
    console.error('Send error:', e.message);
    res.status(500).json({ ok: false, error: e.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
