#!/usr/bin/env python3
"""
🔥 NEXUS JWT TOKEN GEN — FAST EDITION ⚡
Ultra-fast JWT generation with caching!
Like freefiremax.pages.dev but YOURS!
"""

import os, sys, json, time, random, hashlib, base64, threading
from datetime import datetime
import requests, urllib3
urllib3.disable_warnings()

from flask import Flask, request, jsonify
from flask_cors import CORS

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
except:
    os.system("pip install pycryptodome -q")
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad

# Protobuf
import importlib.util
pb2_dir = os.path.join(os.path.dirname(__file__), "pb2")
spec = importlib.util.spec_from_file_location("MajoRLoGinrEq_pb2", 
    os.path.join(pb2_dir, "MajoRLoGinrEq_pb2.py"))
MajoRLoGinrEq_pb2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MajoRLoGinrEq_pb2)
MajorLoginMsg = MajoRLoGinrEq_pb2.MajorLogin

spec2 = importlib.util.spec_from_file_location("MajorLoginRes_pb2",
    os.path.join(pb2_dir, "MajorLoginRes_pb2.py"))
MajorLoginRes_pb2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(MajorLoginRes_pb2)
MajorLoginResMsg = MajorLoginRes_pb2.MajorLoginRes

# ============ CONFIG ============
API_KEY = os.environ.get("API_KEY", "nexus_jwt_key_2026")
AES_KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
AES_IV = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
APP_ID = "100067"
CONNECT = "https://100067.connect.garena.com"
LOGINBP = "https://loginbp.ggpolarbear.com"
CREDIT = "NEXUS JWT TOKEN GEN"

app = Flask(__name__)
CORS(app)

# ============ JWT CACHE ⚡ ============
jwt_cache = {}  # {uid_password_hash: {"jwt": "...", "open_id": "...", "time": timestamp}}
cache_lock = threading.Lock()
CACHE_TTL = 3600  # 1 hour

def get_cached(uid, password):
    key = f"{uid}:{password[:16]}"
    with cache_lock:
        if key in jwt_cache:
            entry = jwt_cache[key]
            if time.time() - entry["time"] < CACHE_TTL:
                return entry
    return None

def set_cache(uid, password, jwt, open_id, account_id):
    key = f"{uid}:{password[:16]}"
    with cache_lock:
        jwt_cache[key] = {
            "jwt": jwt,
            "open_id": open_id,
            "account_id": account_id,
            "time": time.time()
        }
    # Clean old entries
    with cache_lock:
        now = time.time()
        expired = [k for k, v in jwt_cache.items() if now - v["time"] > CACHE_TTL]
        for k in expired:
            del jwt_cache[k]

# ============ HELPERS ============
def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest().upper()

def aes_encrypt(data):
    c = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return c.encrypt(pad(data, AES.block_size))

def aes_decrypt(data):
    c = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return unpad(c.decrypt(data), AES.block_size)

# ============ CORE ============
def register_guest(password):
    r = requests.post(f"{CONNECT}/api/v2/oauth/guest:register",
        json={"app_id": int(APP_ID), "client_type": 2, "password": password, "source": 2},
        headers={"User-Agent": "GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)"}, timeout=10)
    if r.status_code != 200:
        return None, f"Register HTTP {r.status_code}"
    try:
        return str(r.json()["data"]["uid"]), None
    except:
        return None, f"Parse error: {r.text[:100]}"

def token_grant(uid, password):
    data = {"uid": uid, "password": password, "response_type": "token",
            "client_type": "2", "client_secret": CLIENT_SECRET, "client_id": APP_ID}
    for attempt in range(3):
        try:
            r = requests.post(f"{CONNECT}/oauth/guest/token/grant", data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded",
                         "User-Agent": "GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)"}, timeout=10)
            if r.status_code == 200:
                d = r.json()
                if d.get("access_token") and d.get("open_id"):
                    return d["access_token"], d["open_id"], None
                return None, None, f"Missing fields"
            if r.status_code == 429:
                time.sleep(2)
                continue
            return None, None, f"Token HTTP {r.status_code}"
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
                continue
            return None, None, str(e)
    return None, None, "Max retries"

def build_major_login(access_token, open_id):
    """Build MajorLogin protobuf with realistic device fingerprint"""
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
    ml.external_storage_total = random.randint(40000,50000)
    ml.external_storage_available = random.randint(30000,40000)
    ml.internal_storage_total = random.randint(2500,3500)
    ml.internal_storage_available = random.randint(700,1500)
    ml.game_disk_storage_available = random.randint(8000,15000)
    ml.game_disk_storage_total = random.randint(25000,35000)
    ml.external_sdcard_avail_storage = random.randint(30000,40000)
    ml.external_sdcard_total_storage = random.randint(40000,50000)
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
    ml.loading_time = random.randint(15000,20000)
    ml.release_channel = "android"
    ml.extra_info = "KqsHT8W93GdcG3ZozENfFwVHtm7qq1eRUNaIDNgRobozIBtLOiYCc4Y6zvvp"
    ml.android_engine_init_flag = random.randint(100000,120000)
    ml.if_push = 1
    ml.is_vpn = 1
    ml.origin_platform_type = "4"
    ml.primary_platform_type = "4"
    
    raw = ml.SerializeToString()
    encrypted = aes_encrypt(raw)
    return encrypted.hex()

def do_major_login(encrypted_payload):
    """Send MajorLogin and extract JWT"""
    headers = {
        "Accept-Encoding": "gzip", "Authorization": "Bearer",
        "Connection": "Keep-Alive", "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue", "ReleaseVersion": "OB54",
        "User-Agent": "BestHTTP/2 v2.4.8",
        "X-GA": "v1 1", "X-Unity-Version": "2018.4.",
    }
    try:
        r = requests.post(f"{LOGINBP}/MajorLogin", headers=headers, 
                         data=encrypted_payload, timeout=15)
        if r.status_code == 200:
            dec = aes_decrypt(r.content)
            res = MajorLoginResMsg()
            res.ParseFromString(dec)
            if res.token:
                return res.token, res.server_url, str(res.account_id), None
            return None, None, None, "No token in response"
        return None, None, None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, None, None, str(e)

# ============ FAST JWT ENDPOINT ⚡ ============
@app.route("/jwttoken")
def jwttoken():
    key = request.args.get("key")
    uid = request.args.get("uid")
    password = request.args.get("password")
    
    if not key or key != API_KEY:
        return jsonify({"success": False, "error": "Invalid API Key"}), 403
    if not uid or not password:
        return jsonify({"error": "Missing uid/password"}), 400
    
    start = time.time()
    
    # ⚡ CHECK CACHE FIRST (instant response!)
    cached = get_cached(uid, password)
    if cached:
        elapsed = f"{time.time()-start:.2f}s"
        return jsonify({
            "success": True, "api": LOGINBP, "credit": CREDIT,
            "processing_time": elapsed, "open_id": cached["open_id"],
            "token": cached["jwt"], "cached": True,
            "player_overview": {"uid": cached["account_id"] or uid, "nickname": "N/A"},
        })
    
    # Not cached — do full flow
    at, oi, err = token_grant(uid, password)
    if err:
        return jsonify({"success": False, "error": err, "processing_time": f"{time.time()-start:.2f}s"}), 401
    
    payload = build_major_login(at, oi)
    jwt, srv, acc_id, err = do_major_login(payload)
    
    elapsed = f"{time.time()-start:.2f}s"
    if jwt:
        # Cache it for next time ⚡
        set_cache(uid, password, jwt, oi, acc_id)
        return jsonify({
            "success": True, "api": LOGINBP, "credit": CREDIT,
            "processing_time": elapsed, "open_id": oi,
            "token": jwt, "cached": False,
            "player_overview": {"uid": acc_id or uid, "nickname": "N/A"},
        })
    
    return jsonify({"success": False, "error": err, "processing_time": elapsed}), 401

# ============ ACCOUNT GENERATION ============
@app.route("/gen")
def gen():
    key = request.args.get("key")
    if not key or key != API_KEY:
        return jsonify({"success": False, "error": "Invalid API Key"}), 403
    
    region = request.args.get("region", "BD").upper()
    nickname = request.args.get("nickname")
    if not nickname:
        p = ["└","┌","╰","╭","★","☆","✦","✧"]
        n = ["Nexus","Dark","Shadow","Blaze","Frost","Storm","Ghost","Pro","King","Ace"]
        nickname = random.choice(p) + random.choice(n) + str(random.randint(100,9999))
    
    raw_pass = f"NEXUS_{random.randint(10000,99999)}"
    pass_hash = sha256(raw_pass)
    
    start = time.time()
    uid, err = register_guest(pass_hash)
    if err:
        return jsonify({"success": False, "error": err}), 500
    
    at, oi, err = token_grant(uid, pass_hash)
    if err:
        return jsonify({"success": False, "error": err, "uid": uid, "password": raw_pass}), 500
    
    payload = build_major_login(at, oi)
    jwt, srv, acc_id, err = do_major_login(payload)
    
    elapsed = f"{time.time()-start:.2f}s"
    result = {
        "success": bool(jwt),
        "processing_time": elapsed,
        "credit": CREDIT,
        "uid": uid, "password": raw_pass, "password_hash": pass_hash,
        "nickname": nickname, "region": region,
        "open_id": oi, "access_token": at, "jwt": jwt,
    }
    if err:
        result["error"] = err
    return jsonify(result)

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "NEXUS JWT TOKEN GEN ⚡",
        "version": "2.0.0",
        "credit": CREDIT,
        "cache_size": len(jwt_cache),
        "endpoints": {
            "jwttoken": "/jwttoken?key=KEY&uid=UID&password=PASS",
            "gen": "/gen?key=KEY&region=BD",
            "health": "/health"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"""
╔══════════════════════════════════════════════╗
║   🔥 NEXUS JWT TOKEN GEN ⚡ FAST EDITION    ║
║   Like freefiremax.pages.dev but YOURS!     ║
║   Port: {port} | Cache: Enabled ({CACHE_TTL}s)  ║
╚══════════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
