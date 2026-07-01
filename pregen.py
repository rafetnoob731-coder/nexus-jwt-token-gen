#!/usr/bin/env python3
"""
🔥 NEXUS JWT PRE-GENERATOR ⚡
Pre-generate JWTs for your accounts so the API returns instantly!
Like freefiremax — instant 0.25s responses!
"""

import os, sys, json, time, random, hashlib, threading
from datetime import datetime

import requests
urllib3.disable_warnings()

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

# Config
AES_KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
AES_IV = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
APP_ID = "100067"
CONNECT = "https://100067.connect.garena.com"
LOGINBP = "https://loginbp.ggpolarbear.com"

# ============ FUNCTIONS ============
def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest().upper()

def aes_encrypt(data):
    c = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return c.encrypt(pad(data, AES.block_size))

def aes_decrypt(data):
    c = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return unpad(c.decrypt(data), AES.block_size)

def register_guest(password):
    r = requests.post(f"{CONNECT}/api/v2/oauth/guest:register",
        json={"app_id": int(APP_ID), "client_type": 2, "password": password, "source": 2},
        headers={"User-Agent": "GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)"}, timeout=10)
    if r.status_code != 200:
        return None
    try:
        return str(r.json()["data"]["uid"])
    except:
        return None

def token_grant(uid, password):
    data = {"uid": uid, "password": password, "response_type": "token",
            "client_type": "2", "client_secret": CLIENT_SECRET, "client_id": APP_ID}
    for _ in range(3):
        try:
            r = requests.post(f"{CONNECT}/oauth/guest/token/grant", data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded",
                         "User-Agent": "GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)"}, timeout=10)
            if r.status_code == 200:
                d = r.json()
                if d.get("access_token") and d.get("open_id"):
                    return d["access_token"], d["open_id"]
            if r.status_code == 429:
                time.sleep(2); continue
            return None, None
        except:
            time.sleep(1)
    return None, None

def build_major_login(access_token, open_id):
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
                return res.token, str(res.account_id)
        return None, None
    except:
        return None, None

def generate_jwt(uid, password):
    """Full flow to generate JWT"""
    start = time.time()
    
    at, oi = token_grant(uid, password)
    if not at:
        return None, None, "Token grant failed"
    
    payload = build_major_login(at, oi)
    jwt, acc_id = do_major_login(payload)
    
    elapsed = time.time() - start
    return jwt, acc_id, f"({elapsed:.2f}s)"

def pregen_accounts(count=5, region="BD"):
    """Pre-generate accounts with JWTs"""
    accounts = []
    print(f"\n🎮 Pre-generating {count} accounts...\n")
    
    for i in range(count):
        raw_pass = f"NEXUS_{random.randint(10000,99999)}"
        pass_hash = sha256(raw_pass)
        
        print(f"  [{i+1}/{count}] Registering...", end=" ", flush=True)
        uid = register_guest(pass_hash)
        if not uid:
            print("❌ Failed")
            continue
        print(f"✅ {uid}")
        
        time.sleep(2)
        
        print(f"         Generating JWT...", end=" ", flush=True)
        jwt, acc_id, info = generate_jwt(uid, pass_hash)
        if jwt:
            print(f"✅ JWT: {jwt[:30]}...")
            accounts.append({
                "uid": uid,
                "password": raw_pass,
                "password_hash": pass_hash,
                "jwt": jwt,
                "account_id": acc_id,
            })
        else:
            print(f"❌ {info}")
        
        time.sleep(1)
    
    return accounts

def save_accounts(accounts, filename="pregen_accounts.json"):
    with open(filename, "w") as f:
        json.dump(accounts, f, indent=2)
    print(f"\n💾 Saved {len(accounts)} accounts to {filename}")

# ============ MAIN ============
if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    
    print(r"""
╔══════════════════════════════════════════════╗
║   🔥 NEXUS JWT PRE-GENERATOR ⚡             ║
║   Pre-gen JWTs for INSTANT responses!       ║
║   Like freefiremax — 0.25s responses!       ║
╚══════════════════════════════════════════════╝
    """)
    
    count = int(input("📊 Number of accounts to pre-gen: ") or "5")
    accounts = pregen_accounts(count)
    save_accounts(accounts)
    
    print(f"\n⚡ {len(accounts)} JWTs ready for instant response!")
    print("📌 Deploy flask_api.py and the cache will serve these instantly!")
