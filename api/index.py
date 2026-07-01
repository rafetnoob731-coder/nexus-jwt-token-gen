"""
🔥 NEXUS JWT TOKEN GEN ⚡
Full JWT generation via MajorLogin protobuf flow
Cached JWTs in 0.03s | Full flow in ~1s
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys, json, time, random, hashlib, base64
from datetime import datetime
import requests, urllib3
urllib3.disable_warnings()

# ============ PROTOBUF IMPORTS ============
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
try:
    from pb2 import MajoRLoGinrEq_pb2
    from pb2 import MajorLoginRes_pb2
    HAS_PROTOBUF = True
except:
    try:
        from google.protobuf import descriptor_pool
        HAS_PROTOBUF = False
    except:
        HAS_PROTOBUF = False

# ============ CRYPTO ============
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    HAS_CRYPTO = True
except:
    HAS_CRYPTO = False

AES_KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
AES_IV = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])

def aes_encrypt(data):
    c = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return c.encrypt(pad(data, AES.block_size))

def aes_decrypt(data):
    c = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return unpad(c.decrypt(data), AES.block_size)

application = Flask(__name__)
CORS(application)

# ============ CONFIG ============
API_KEY = os.environ.get("API_KEY", "nexus_jwt_key_2026")
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
APP_ID = "100067"
CONNECT = "https://100067.connect.garena.com"
LOGINBP_HOSTS = [
    "loginbp.ggpolarbear.com",  # Polarbear
    "loginbp.ggblueshark.com",  # Blueshark
    "loginbp.common.ggbluefox.com",  # Bluefox
]
LOGINBP = "https://" + LOGINBP_HOSTS[0]
CREDIT = "NEXUS JWT TOKEN GEN"

# ============ JWT CACHE ⚡ ============
jwt_cache = {}
CACHE_TTL = 3600

def get_cached(uid, password):
    key = f"{uid}:{password[:16]}"
    entry = jwt_cache.get(key)
    if entry and time.time() - entry["time"] < CACHE_TTL:
        return entry
    return None

def set_cache(uid, password, jwt, open_id, account_id):
    key = f"{uid}:{password[:16]}"
    jwt_cache[key] = {"jwt": jwt, "open_id": open_id, "account_id": account_id, "time": time.time()}
    # Clean expired
    now = time.time()
    for k in list(jwt_cache.keys()):
        if now - jwt_cache[k]["time"] > CACHE_TTL:
            del jwt_cache[k]

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest().upper()

# ============ CORE API ============
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
    if not HAS_PROTOBUF or not HAS_CRYPTO:
        return None, "Missing protobuf or crypto modules"
    
    ml = MajoRLoGinrEq_pb2.MajorLogin()
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
    return encrypted.hex(), None

def do_major_login(encrypted_payload):
    """Send MajorLogin to all loginbp hosts, try each until one works"""
    headers = {
        "Accept-Encoding": "gzip", "Authorization": "Bearer",
        "Connection": "Keep-Alive", "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue", "ReleaseVersion": "OB54",
        "User-Agent": "BestHTTP/2 v2.4.8",
        "X-GA": "v1 1", "X-Unity-Version": "2018.4.",
    }
    errors = []
    for host in LOGINBP_HOSTS:
        url = f"https://{host}/MajorLogin"
        try:
            r = requests.post(url, headers=headers,
                             data=encrypted_payload, timeout=15)
            if r.status_code == 200:
                try:
                    dec = aes_decrypt(r.content)
                    res = MajorLoginRes_pb2.MajorLoginRes()
                    res.ParseFromString(dec)
                    if res.token:
                        return res.token, res.server_url, str(res.account_id), None, host
                    errors.append(f"{host}: no token in response")
                except Exception as e:
                    errors.append(f"{host}: decrypt/parse error: {e}")
            else:
                errors.append(f"{host}: HTTP {r.status_code}")
        except Exception as e:
            errors.append(f"{host}: {e}")
    return None, None, None, "; ".join(errors), None

# ============ ROUTES ============
@application.route("/api")
@application.route("/api/health")
def health():
    return jsonify({
        "status": "ok", "service": CREDIT, "version": "2.0.0",
        "modules": {"protobuf": HAS_PROTOBUF, "crypto": HAS_CRYPTO},
        "cache_size": len(jwt_cache),
        "endpoints": {
            "jwttoken": "/api/jwttoken?key=KEY&uid=UID&password=PASS",
            "gen": "/api/gen?key=KEY&region=BD"
        }
    })

@application.route("/api/jwttoken")
def jwttoken():
    key = request.args.get("key")
    uid = request.args.get("uid")
    password = request.args.get("password")
    
    if not key or key != API_KEY:
        return jsonify({"success": False, "error": "Invalid API Key"}), 403
    if not uid or not password:
        return jsonify({"error": "Missing uid/password"}), 400
    
    start = time.time()
    
    # ⚡ CACHE CHECK
    cached = get_cached(uid, password)
    if cached:
        return jsonify({
            "success": True, "credit": CREDIT,
            "processing_time": f"{time.time()-start:.2f}s",
            "open_id": cached["open_id"], "uid": uid,
            "jwt": cached["jwt"], "cached": True
        })
    
    # Step 1: Token grant
    at, oi, err = token_grant(uid, password)
    if err:
        return jsonify({"success": False, "error": err}), 401
    
    # Step 2: Try MajorLogin for real JWT
    jwt = None
    account_id = None
    server_url = None
    major_error = None
    
    if HAS_PROTOBUF and HAS_CRYPTO:
        payload, build_err = build_major_login(at, oi)
        if payload:
            jwt, server_url, account_id, major_err, host_used = do_major_login(payload)
            major_error = major_err
        else:
            major_error = build_err
    else:
        major_error = f"Missing modules: protobuf={HAS_PROTOBUF}, crypto={HAS_CRYPTO}"
    
    # Step 3: Fallback if MajorLogin failed
    if not jwt:
        # MajorLogin failed — use access_token as fallback
        jwt = at
    
    elapsed = f"{time.time()-start:.2f}s"
    
    if account_id:
        set_cache(uid, password, jwt, oi, account_id)
    
    response = {
        "success": True, "credit": CREDIT,
        "processing_time": elapsed,
        "open_id": oi, "uid": uid,
        "jwt": jwt,
        "note": "The jwt field contains your game authentication token. If it's a 64-char hex string, that's the access_token (MajorLogin from Vercel IP may be restricted). If it starts with 'eyJ', it's the full JWT.",
    }
    
    if server_url:
        response["server_url"] = server_url
    if account_id:
        response["account_id"] = account_id
    if host_used:
        response["majorlogin_host"] = f"https://{host_used}/MajorLogin"
    if major_error:
        response["majorlogin_error"] = major_error
    
    return jsonify(response)

@application.route("/api/gen")
def gen():
    key = request.args.get("key")
    if not key or key != API_KEY:
        return jsonify({"success": False, "error": "Invalid API Key"}), 403
    
    region = request.args.get("region", "BD").upper()
    raw_pass = f"NEXUS_{random.randint(10000, 99999)}"
    pass_hash = sha256(raw_pass)
    
    start = time.time()
    uid, err = register_guest(pass_hash)
    if err:
        return jsonify({"success": False, "error": err}), 500
    
    at, oi, err = token_grant(uid, pass_hash)
    if err:
        return jsonify({"success": False, "error": err, "uid": uid, "password": raw_pass}), 500
    
    # Try MajorLogin
    jwt = at
    account_id = None
    if HAS_PROTOBUF and HAS_CRYPTO:
        payload, _ = build_major_login(at, oi)
        if payload:
            jwt, _, account_id, _, _ = do_major_login(payload) or (at, None, None, None, None)
    
    return jsonify({
        "success": True, "credit": CREDIT,
        "processing_time": f"{time.time()-start:.2f}s",
        "uid": uid, "password": raw_pass,
        "open_id": oi, "account_id": account_id or uid,
        "jwt": jwt if jwt else at,
        "region": region
    })
