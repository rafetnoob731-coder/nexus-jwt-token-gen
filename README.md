# 🔥 NEXUS JWT TOKEN GEN

Your own private JWT token generator for Free Fire.
Like `freefiremax.pages.dev` but YOURS, with NEXUS branding.

## 🚀 Deployment Options

### Option 1: Python API (Local/VPS)

```bash
cd nexusjwttokengen
pip install flask pycryptodome requests protobuf
python flask_api.py
```

### Option 2: Cloudflare Worker (RECOMMENDED)

```bash
cd cloudflare-worker
npm install -g wrangler
wrangler login
wrangler deploy
```

## 📌 API Usage

### Generate JWT
```
GET /jwttoken?key=nexus_key&uid=UID&password=PASSWORD
```

### Generate Fresh Account + JWT
```
GET /gen?key=nexus_key&region=BD&nickname=MyNick
```

### Health Check
```
GET /health
```

## 📊 Response Example

```json
{
  "success": true,
  "api": "https://loginbp.ggpolarbear.com",
  "credit": "NEXUS JWT TOKEN GEN",
  "processing_time": "2.34s",
  "open_id": "85b4acbe...",
  "token": "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ...",
  "cached": false,
  "player_overview": {
    "uid": "5436729136",
    "nickname": "N/A"
  }
}
```

## 🔐 Security
- Set `API_KEY` env var to secure your API
- Default key: `nexus_jwt_key_2026`
- Always change in production!

## ⚡ Credit
NEXUS JWT TOKEN GENERATOR
