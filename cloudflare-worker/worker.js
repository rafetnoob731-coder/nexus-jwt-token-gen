// ============================================
// NEXUS JWT TOKEN GEN — Cloudflare Worker
// Deploy: wrangler deploy
// ============================================

const CREDIT = 'NEXUS JWT TOKEN GEN';
const LOGINBP = 'loginbp.ggpolarbear.com';
const CONNECT = '100067.connect.garena.com';
const CLIENT_SECRET = '2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3';
const AES_KEY = new Uint8Array([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56]);
const AES_IV = new Uint8Array([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37]);
const APP_ID = '100067';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const API_KEY = env.API_KEY || 'nexus_jwt_key_2026';
    const start = Date.now();

    const cors = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET,OPTIONS',
      'Access-Control-Allow-Headers': '*',
      'Content-Type': 'application/json',
    };
    if (request.method === 'OPTIONS') return new Response(null, {headers: cors});

    try {
      // Health
      if (path === '/health') {
        return json({status: 'ok', service: CREDIT, version: '1.0.0'}, cors);
      }

      // Auth
      const key = url.searchParams.get('key');
      if (!key || key !== API_KEY) {
        return json({success: false, error: 'Invalid API Key'}, cors, 403);
      }

      // === JWT TOKEN ENDPOINT ===
      if (path === '/jwttoken') {
        const uid = url.searchParams.get('uid');
        const password = url.searchParams.get('password');

        if (!uid || !password) {
          return json({error: 'Missing uid/password'}, cors, 400);
        }

        // Step 1: Token Grant
        const tokenBody = new URLSearchParams({
          uid, password, response_type: 'token',
          client_type: '2', client_secret: CLIENT_SECRET, client_id: APP_ID
        }).toString();

        let at, oi;
        for (let i = 0; i < 5; i++) {
          await sleep(1500);
          const tr = await fetch(`https://${CONNECT}/oauth/guest/token/grant`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              'User-Agent': 'GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)'
            },
            body: tokenBody
          });
          if (tr.ok) {
            const td = await tr.json();
            if (td.access_token && td.open_id) { at = td.access_token; oi = td.open_id; break; }
          } else if (tr.status === 429) { await sleep(3000); }
          else { break; }
        }

        if (!at || !oi) {
          return json({error: 'Token grant failed'}, cors, 401);
        }

        // Step 2: MajorLogin → JWT
        const payload = await buildMajorLogin(at, oi);
        const jwt = await doMajorLogin(payload);
        const elapsed = ((Date.now() - start) / 1000).toFixed(2);

        if (jwt) {
          return json({
            success: true, api: `https://${LOGINBP}`, credit: CREDIT,
            processing_time: `${elapsed}s`, open_id: oi, token: jwt, cached: false,
            player_overview: { uid, nickname: 'N/A' }
          }, cors);
        }
        return json({error: 'JWT generation failed', processing_time: `${elapsed}s`}, cors, 401);
      }

      // === GENERATE ACCOUNT + JWT ===
      if (path === '/gen') {
        const region = (url.searchParams.get('region') || 'BD').toUpperCase();
        const nickname = url.searchParams.get('nickname') || genNick();
        const rawPass = url.searchParams.get('password') || genPass();
        const passHash = await sha256(rawPass);

        // Register
        const reg = await register(passHash);
        if (!reg.success) return json({error: reg.error}, cors, 500);

        await sleep(2000);

        // Token Grant
        const tokenBody = new URLSearchParams({
          uid: reg.uid, password: passHash, response_type: 'token',
          client_type: '2', client_secret: CLIENT_SECRET, client_id: APP_ID
        }).toString();
        
        let at, oi;
        for (let i = 0; i < 5; i++) {
          await sleep(1500);
          const tr = await fetch(`https://${CONNECT}/oauth/guest/token/grant`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              'User-Agent': 'GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)'
            },
            body: tokenBody
          });
          if (tr.ok) { const td = await tr.json(); if (td.access_token && td.open_id) { at = td.access_token; oi = td.open_id; break; } }
          else if (tr.status === 429) await sleep(3000);
          else break;
        }

        // MajorLogin
        let jwt = null;
        if (at && oi) {
          await sleep(1000);
          const payload = await buildMajorLogin(at, oi);
          jwt = await doMajorLogin(payload);
        }

        const elapsed = ((Date.now() - start) / 1000).toFixed(2);
        return json({
          success: true, processing_time: `${elapsed}s`, credit: CREDIT,
          uid: reg.uid, password: rawPass, password_hash: passHash,
          nickname, region, open_id: oi, access_token: at, jwt,
        }, cors);
      }

      return json({error: 'Not Found', endpoints: {health: '/health', jwttoken: '/jwttoken?key=KEY&uid=UID&password=PASS', gen: '/gen?key=KEY'}}, cors, 404);

    } catch (err) {
      return json({success: false, error: err.message}, cors, 500);
    }
  }
};

async function register(password) {
  const r = await fetch(`https://${CONNECT}/api/v2/oauth/guest:register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'User-Agent': 'GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)',
    },
    body: JSON.stringify({app_id: parseInt(APP_ID), client_type: 2, password, source: 2})
  });
  if (r.ok) { const d = await r.json(); if (d?.data?.uid) return {success: true, uid: String(d.data.uid)}; }
  return {success: false, error: `Register failed: ${r.status}`};
}

async function buildMajorLogin(accessToken, openId) {
  const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
  // Build protobuf manually (minimal fields)
  const fields = [
    [1, now],
    [3, '1.126.6'],
    [5, 1],
    [7, 4],
    [8, accessToken, 'bytes'],
    [9, openId, 'bytes'],
  ];
  const payload = buildProto(fields);
  return await aesEncrypt(payload);
}

async function doMajorLogin(encryptedHex) {
  const r = await fetch(`https://${LOGINBP}/MajorLogin`, {
    method: 'POST',
    headers: {
      'Accept-Encoding': 'gzip', 'Authorization': 'Bearer', 'Connection': 'Keep-Alive',
      'Content-Type': 'application/x-www-form-urlencoded', 'Expect': '100-continue',
      'ReleaseVersion': 'OB54', 'User-Agent': 'BestHTTP/2 v2.4.8',
      'X-GA': 'v1 1', 'X-Unity-Version': '2018.4.',
    },
    body: encryptedHex,
  });
  if (r.ok) {
    const buf = await r.arrayBuffer();
    const dec = await aesDecrypt(new Uint8Array(buf));
    // Extract JWT from decrypted response
    const text = new TextDecoder().decode(dec);
    const match = text.match(/eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/);
    if (match) return match[0];
  }
  return null;
}

function buildProto(fields) {
  const parts = [];
  for (const [num, value, type] of fields) {
    const idx = num << 3;
    if (type === 'bytes' || typeof value === 'string') {
      const enc = new TextEncoder().encode(String(value));
      parts.push(encodeVarint(idx | 2), encodeVarint(enc.length), enc);
    } else if (typeof value === 'number') {
      parts.push(encodeVarint(idx | 0), encodeVarint(value));
    }
  }
  return concat(...parts);
}

function encodeVarint(n) {
  const b = [];
  while (n >= 0x80) { b.push((n & 0x7F) | 0x80); n >>>= 7; }
  b.push(n & 0x7F);
  return new Uint8Array(b);
}

function concat(...arrays) {
  let len = 0;
  for (const a of arrays) len += a.length;
  const r = new Uint8Array(len); let off = 0;
  for (const a of arrays) { r.set(a, off); off += a.length; }
  return r;
}

async function aesEncrypt(data) {
  const key = await crypto.subtle.importKey('raw', AES_KEY, {name: 'AES-CBC'}, false, ['encrypt']);
  const enc = await crypto.subtle.encrypt({name: 'AES-CBC', iv: AES_IV}, key, data);
  return Array.from(new Uint8Array(enc)).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function aesDecrypt(data) {
  const key = await crypto.subtle.importKey('raw', AES_KEY, {name: 'AES-CBC'}, false, ['decrypt']);
  const dec = await crypto.subtle.decrypt({name: 'AES-CBC', iv: AES_IV}, key, data);
  return new Uint8Array(dec);
}

async function sha256(str) {
  const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
  return Array.from(new Uint8Array(h)).map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
}

function genNick() {
  const p = ['└','┌','╰','╭','★','☆','✦','✧'];
  const n = ['Nexus','Dark','Shadow','Blaze','Frost','Storm','Ghost','Pro','King','Ace'];
  return p[Math.random()*p.length|0] + n[Math.random()*n.length|0] + (Math.random()*9999|0);
}

function genPass() {
  const c = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let r = 'NEXUS_';
  for (let i = 0; i < 12; i++) r += c[Math.random()*c.length|0];
  return r;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function json(data, headers, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {status, headers});
}
