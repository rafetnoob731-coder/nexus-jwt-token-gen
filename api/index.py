"""
🔥 NEXUS JWT TOKEN GEN — Vercel Serverless
Access at: /api/health, /api/jwttoken?key=KEY&uid=UID&password=PASS
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os, time, json, hashlib, requests
import urllib3
urllib3.disable_warnings()

app = Flask(__name__)
CORS(app)
application = app  # Vercel looks for 'application'

API_KEY = os.environ.get("API_KEY", "nexus_jwt_key_2026")
CREDIT = "NEXUS JWT TOKEN GEN"
CONNECT = "https://100067.connect.garena.com"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
APP_ID = "100067"

@app.route("/api")
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": CREDIT, "version": "2.0.0"})

@app.route("/api/jwttoken")
def jwttoken():
    key = request.args.get("key")
    uid = request.args.get("uid")
    password = request.args.get("password")
    if not key or key != API_KEY:
        return jsonify({"success": False, "error": "Invalid API Key"}), 403
    if not uid or not password:
        return jsonify({"error": "Missing uid/password"}), 400
    
    start = time.time()
    try:
        r = requests.post(f"{CONNECT}/oauth/guest/token/grant",
            data={"uid": uid, "password": password, "response_type": "token",
                  "client_type": "2", "client_secret": CLIENT_SECRET, "client_id": APP_ID},
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "User-Agent": "GarenaMSDK/4.0.39"}, timeout=10)
        if r.status_code != 200:
            return jsonify({"success": False, "error": f"Token: HTTP {r.status_code}"}), 401
        d = r.json()
        elapsed = f"{time.time()-start:.2f}s"
        return jsonify({
            "success": True, "credit": CREDIT, "processing_time": elapsed,
            "open_id": d.get("open_id"), "uid": uid,
            "jwt": d.get("access_token"),
            "note": "jwt = access_token — use this to authenticate Free Fire API calls"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
