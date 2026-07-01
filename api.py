#!/usr/bin/env python3
"""
🔥 NEXUS JWT TOKEN GENERATOR
Self-hosted API — Generate Free Fire JWT tokens instantly
Similar to freefiremax.pages.dev but yours!

Usage:
  python api.py
  
  GET /jwttoken?key=YOUR_KEY&uid=UID&password=PASSWORD
  GET /gen?key=YOUR_KEY&region=BD
  GET /health
"""

import os
import sys
import json
import time
import random
import string
import hashlib
import base64
import re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Crypto
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
except ImportError:
    os.system("pip install pycryptodome -q")
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad

# Protobuf
import importlib.util
spec = importlib.util.spec_from_file_location("MajoRLoGinrEq_pb2",
    os.path.join(os.path.dirname(__file__), "pb2", "MajoRLoGinrEq_pb2.py"))
MajoRLoGinrEq_pb2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MajoRLoGinrEq_pb2)

spec2 = importlib.util.spec_from_file_location("MajorLoginRes_pb2",
    os.path.join(os.path.dirname(__file__), "pb2", "MajorLoginRes_pb2.py"))
MajorLoginRes_pb2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(MajorLoginRes_pb2)

MajorLoginMsg = MajoRLoGinrEq_pb2.MajorLogin
MajorLoginResMsg = MajorLoginRes_pb2.MajorLoginRes

import requests
import urllib3
urllib3.disable_warnings()

# ==================== CONFIG ====================
API_KEY = os.environ.get("API_KEY", "nexus_jwt_key_2026")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8001))

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
APP_ID = "100067"
CONNECT_URL = "https://100067.connect.garena.com"
LOGINBP_URL = "https://loginbp.ggpolarbear.com"
CREDIT = "NEXUS JWT TOKEN GEN"

# ==================== CRYPTO ====================
def aes_encrypt(data):
    c = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return c.encrypt(pad(data, AES.block_size))

def aes_decrypt(data):
    c = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return c.decrypt(data)

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest().upper()

# ==================== API FUNCTIONS ====================
def register_guest(password):
    """Register a new guest account"""
    r = requests.post(f"{CONNECT_URL}/api/v2/oauth/guest:register",
        json={"app_id": int(APP_ID), "client_type": 2, "password": password, "source": 2},
        headers={"User-Agent": "GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)"},
        timeout=10)
    if r.status_code != 200:
        return None, f"Register failed: {r.status_code}"
    try:
        uid = str(r.json()["data"]["uid"])
        return uid, None
    except:
        return None, f"Register parse error: {r.text[:100]}"

def token_grant(uid, password):
    """Get access token + open_id from Garena Connect"""
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": CLIENT_SECRET,
        "client_id": APP_ID,
    }
    for attempt in range(5):
        try:
            time.sleep(1.5)
            r = requests.post(f"{CONNECT_URL}/oauth/guest/token/grant",
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)",
                }, timeout=10)
            if r.status_code == 200:
                d = r.json()
                if d.get("access_token") and d.get("open_id"):
                    return d["access_token"], d["open_id"], None
                return None, None, f"Missing fields: {d}"
            if r.status_code == 429:
                time.sleep(3)
                continue
            return None, None, f"Token HTTP {r.status_code}: {r.text[:100]}"
        except Exception as e:
            if attempt < 4:
                time.sleep(2)
                continue
            return None, None, str(e)
    return None, None, "Max retries"

def build_major_login(access_token, open_id):
    """Build the MajorLogin protobuf payload"""
    ml = MajorLoginMsg()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    ml.event_time = now
    ml.game_name = "free fire"
    ml.platform_id = 1
    ml.client_version = "1.126.5"
    ml.system_software = "Android OS 11 / API-30 (RQ3A.211001.001)"
    ml.system_hardware = "Handheld"
    ml.telecom_operator = "GrameenPhone"
    ml.network_type = "WIFI"
    ml.screen_width = 2400
    ml.screen_height = 1080
    ml.screen_dpi = "320"
    ml.processor_details = "ARMv8-A 2.9GHz | 8"
    ml.memory = 4096
    ml.gpu_renderer = "Mali-G78 MP14"
    ml.gpu_version = "OpenGL ES 3.2"
    ml.unique_device_id = f"Samsung|{hashlib.md5(str(random.random()).encode()).hexdigest()}"
    ml.client_ip = "10.0.2.15"
    ml.language = "en"
    ml.open_id = open_id
    ml.open_id_type = "4"
    ml.device_type = "Handheld"
    ml.access_token = access_token
    ml.platform_sdk_id = 1
    ml.network_operator_a = "GrameenPhone"
    ml.network_type_a = "WIFI"
    ml.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    ml.external_storage_total = random.randint(40000, 50000)
    ml.external_storage_available = random.randint(30000, 40000)
    ml.internal_storage_total = random.randint(2500, 3500)
    ml.internal_storage_available = random.randint(700, 1500)
    ml.game_disk_storage_available = random.randint(8000, 15000)
    ml.game_disk_storage_total = random.randint(25000, 35000)
    ml.external_sdcard_avail_storage = random.randint(30000, 40000)
    ml.external_sdcard_total_storage = random.randint(40000, 50000)
    ml.login_by = 1
    ml.library_path = "/data/app/com.dts.freefireth/lib/arm"
    ml.reg_avatar = 1
    ml.library_token = f"{hashlib.md5(b'123456').hexdigest()}|/data/app/com.dts.freefireth/base.apk"
    ml.channel_type = 6
    ml.cpu_type = 1
    ml.cpu_architecture = "64"
    ml.client_version_code = "2019119026"
    ml.graphics_api = "OpenGLES2"
    ml.supported_astc_bitset = 255
    ml.login_open_id_type = 4
    ml.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    ml.loading_time = random.randint(15000, 20000)
    ml.release_channel = "android"
    ml.extra_info = "KqsHT8W93GdcG3ZozENfFwVHtm7qq1eRUNaIDNgRobozIBtLOiYCc4Y6zvvp"
    ml.android_engine_init_flag = random.randint(100000, 120000)
    ml.if_push = 1
    ml.is_vpn = 1
    ml.origin_platform_type = "4"
    ml.primary_platform_type = "4"
    
    raw = ml.SerializeToString()
    encrypted = aes_encrypt(raw)
    return encrypted.hex()

def major_login(encrypted_payload):
    """Send MajorLogin to LoginBP and get JWT"""
    headers = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "ReleaseVersion": "OB54",
        "User-Agent": "BestHTTP/2 v2.4.8",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4.",
    }
    try:
        r = requests.post(f"{LOGINBP_URL}/MajorLogin",
            headers=headers, data=encrypted_payload, timeout=15)
        
        if r.status_code == 200:
            # Decrypt response
            dec = aes_decrypt(r.content)
            # Remove PKCS7 padding
            pad_len = dec[-1]
            dec = dec[:-pad_len]
            
            # Parse protobuf
            res = MajorLoginResMsg()
            res.ParseFromString(dec)
            
            if res.token:
                return res.token, res.server_url, None
            return None, None, f"No token in response"
        else:
            return None, None, f"MajorLogin HTTP {r.status_code}: {r.content[:100]}"
    except Exception as e:
        return None, None, str(e)

def generate_full_account(region="BD", nickname=None):
    """Full flow: Register → Token → MajorRegister → MajorLogin → JWT"""
    # Generate credentials
    if not nickname:
        prefixes = ['└', '┌', '╰', '╭', '★', '☆', '✦', '✧']
        names = ['Nexus', 'Dark', 'Shadow', 'Blaze', 'Frost', 'Storm', 'Ghost', 'Pro', 'King', 'Ace']
        nickname = random.choice(prefixes) + random.choice(names) + str(random.randint(100, 9999))
    
    raw_password = f"NEXUS_{random.randint(10000, 99999)}"
    password_hash = sha256(raw_password)
    
    # Register
    uid, err = register_guest(password_hash)
    if err:
        return {"success": False, "error": err}
    
    time.sleep(2)
    
    # Token grant
    at, oi, err = token_grant(uid, password_hash)
    if err:
        return {"success": False, "error": err, "uid": uid, "password": raw_password}
    
    time.sleep(1)
    
    # MajorLogin
    payload = build_major_login(at, oi)
    jwt, server_url, err = major_login(payload)
    
    result = {
        "success": True if jwt else False,
        "uid": uid,
        "password": raw_password,
        "password_hash": password_hash,
        "nickname": nickname,
        "region": region,
        "open_id": oi,
        "access_token": at,
        "jwt": jwt,
        "server_url": server_url,
        "credit": CREDIT,
    }
    if err:
        result["error"] = err
    return result

def get_jwt(uid, password):
    """Get JWT for existing account: Token → MajorLogin"""
    start_time = time.time()
    
    # Token grant  
    at, oi, err = token_grant(uid, password)
    if err:
        return {"success": False, "error": err}
    
    time.sleep(1)
    
    # MajorLogin
    payload = build_major_login(at, oi)
    jwt, server_url, err = major_login(payload)
    
    elapsed = round(time.time() - start_time, 2)
    
    if jwt:
        return {
            "success": True,
            "api": LOGINBP_URL,
            "credit": CREDIT,
            "processing_time": f"{elapsed}s",
            "open_id": oi,
            "token": jwt,
            "cached": False,
            "player_overview": {
                "uid": uid,
                "nickname": "N/A",
            }
        }
    return {"success": False, "error": err, "processing_time": f"{elapsed}s"}

# ==================== HTTP SERVER ====================
class JWTAPIHandler(BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)
        
        # Extract params
        key = params.get("key", [None])[0]
        uid = params.get("uid", [None])[0]
        password = params.get("password", [None])[0]
        access_token = params.get("access_token", [None])[0]
        open_id = params.get("open_id", [None])[0]
        eat = params.get("eat", [None])[0]
        region = params.get("region", ["BD"])[0]
        nickname = params.get("nickname", [None])[0]
        
        # Health check
        if path in ["", "/", "/health"]:
            return self._json({
                "status": "ok",
                "service": "NEXUS JWT Token Gen",
                "version": "1.0.0",
                "credit": CREDIT,
                "endpoints": {
                    "jwt": "/jwttoken?key=KEY&uid=UID&password=PASS",
                    "gen": "/gen?key=KEY&region=BD",
                    "health": "/health"
                }
            })
        
        # Auth check
        if not key or key != API_KEY:
            return self._json({"success": False, "error": "Invalid API Key"}, 403)
        
        # Generate JWT
        if path == "/jwttoken":
            if not uid or not password:
                return self._json({
                    "error": "Missing parameters. Use: &uid=UID&password=PASSWORD"
                }, 400)
            
            result = get_jwt(uid, password)
            return self._json(result, 200 if result.get("success") else 401)
        
        # Generate full account + JWT
        if path == "/gen":
            result = generate_full_account(region.upper(), nickname)
            return self._json(result, 200 if result.get("success") else 500)
        
        # 404
        return self._json({"error": "Not Found"}, 404)
    
    def log_message(self, format, *args):
        # Clean logging
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]} {args[2]}")

def main():
    print(f"""
╔══════════════════════════════════════════════╗
║     🔥 NEXUS JWT TOKEN GENERATOR v1.0       ║
║     Generate Free Fire JWTs instantly        ║
║     Running on http://{HOST}:{PORT}              ║
╚══════════════════════════════════════════════╝

📌 Endpoints:
   GET /jwttoken?key={API_KEY}&uid=UID&password=PASS
   GET /gen?key={API_KEY}&region=BD
   GET /health

⚡ Credit: {CREDIT}
""")
    
    server = HTTPServer((HOST, PORT), JWTAPIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        server.server_close()

if __name__ == "__main__":
    main()
