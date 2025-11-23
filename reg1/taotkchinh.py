import requests
import time
import json
import random
import secrets
import string
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
from bypass_datadom import DataDome
from mailao import tempmail


class GarenaRegister:
    PUBLIC_KEY_GARENA = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDR7FHnzqB8syM62mAJAG7z6/ie
/Vz3eq0hEFHQCAd9xxQocrjDbulx1LNox5wTprvLibVRqDCMaPcXZMFRnerZC1YO
Ems2U3VwDMWi5s+B4qD+6jG1PB+NPzrlIt+asZtcDDkdmX1t5WgHMoubvV9tCOpH
YUBgF34S9lvbldXW4wIDAQAB
-----END PUBLIC KEY-----"""

    def __init__(self):
        """Khởi tạo session và header gốc"""
        self.session = requests.Session()
        self.headers = self._get_base_headers()

        # ---- Random hóa User-Agent để giảm fingerprinting ----
        ua_choices = [
            "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        ]
        try:
            chosen_ua = random.choice(ua_choices)
            self.headers['User-Agent'] = chosen_ua
            self.session.headers.update({'User-Agent': chosen_ua})
        except Exception:
            pass

    def _get_base_headers(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Host": "100054.connect.garena.com",
            "Origin": "https://100054.connect.garena.com",
            "Referer": "https://100054.connect.garena.com/universal/register?redirect_uri=https://100054.connect.garena.com/universal/oauth?redirect_uri=gop100054%253A%252F%252Fauth%252F%26response_type=code%26client_id=100054%26login_scenario=normal%26locale=vi_VN&locale=vi_VN",
            "sec-ch-ua": '"Chromium";v="124", "Android WebView";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-G975N Build/PQ3A.190705.09121607; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.82 Mobile Safari/537.36",
            "X-Requested-With": "com.garena.game.kgvn",
        }

    def _get_datadome_cookie(self, proxy=None, port=None):
        """Lấy cookie datadome hợp lệ"""
        dd = DataDome()
        headers, payload = dd.build("https://100054.connect.garena.com/")
        url = "https://dd.garena.com/js/"

        proxies = None
        if proxy and port:
            proxies = {
                "http": f"http://{proxy}:{port}",
                "https": f"http://{proxy}:{port}"
            }

        try:
            r = self.session.post(url, proxies=proxies, headers=headers, data=payload, timeout=30)
            response_json = json.loads(r.text)
            cookie_str = response_json.get("cookie", "")
            if "datadome=" in cookie_str:
                self.session.headers.update({"Cookie": cookie_str})
                print(f"✅ Datadome: {cookie_str}")
                return True
        except Exception as e:
            print("❌ Parse error:", e)

        print("❌ Failed to get datadome cookie!")
        return False

    def _encrypt_password_with_rsa(self, password_plaintext):
        try:
            key = RSA.import_key(self.PUBLIC_KEY_GARENA)
            cipher = PKCS1_v1_5.new(key)
            encrypted_password = cipher.encrypt(password_plaintext.encode('utf-8'))
            return encrypted_password.hex()
        except Exception as e:
            print(f"❌ Encryption error: {e}")
            return None

    def send_email_otp(self, username, email, proxy=None, port=None):
        """Gửi yêu cầu OTP đăng ký qua email (có delay và random UA)."""
        self._get_datadome_cookie(proxy, port)
        timestamp = round(time.time() * 1000)

        proxies = None
        if proxy and port:
            proxies = {
                "http": f"http://{proxy}:{port}",
                "https": f"http://{proxy}:{port}"
            }

        url = "https://100054.connect.garena.com/api/send_register_code_email"
        data = {
            "username": username,
            "email": email,
            "locale": "vi-VN",
            "format": "json",
            "id": timestamp
        }

        # ---- Random hóa User-Agent mỗi lần gửi OTP ----
        ua_choices = [
            "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        ]
        try:
            random_ua = random.choice(ua_choices)
            self.session.headers.update({'User-Agent': random_ua})
        except Exception:
            pass

        # ---- Thêm delay ngẫu nhiên 3–7s ----
        try:
            delay = round(random.uniform(3, 7), 2)
            print(f"⏳ Đang chờ {delay}s trước khi gửi OTP (chống spam)...")
            time.sleep(delay)
        except Exception:
            pass

        print(f"✅ Sending OTP request to: {url}")
        response = self.session.post(url, proxies=proxies, headers=self.headers, data=data)
        print("Status code:", response.status_code)
        print("Response body:", response.text)

        return response.json() if response.ok else None

    def register_account(self, username, email, email_otp, passw, proxy=None, port=None, location="VN", locale="vi-VN", redirect_uri=""):
        """Gửi yêu cầu tạo tài khoản Garena."""
        self._get_datadome_cookie(proxy, port)
        encrypted_password = self._encrypt_password_with_rsa(passw)
        if not encrypted_password:
            return

        timestamp = round(time.time() * 1000)
        url = "https://100054.connect.garena.com/api/register"

        proxies = None
        if proxy and port:
            proxies = {
                "http": f"http://{proxy}:{port}",
                "https": f"http://{proxy}:{port}"
            }

        data = {
            "username": username,
            "email": email,
            "email_otp": email_otp,
            "password": encrypted_password,
            "location": location,
            "locale": locale,
            "redirect_uri": redirect_uri,
            "format": "json",
            "id": timestamp
        }

        response = self.session.post(url, proxies=proxies, headers=self.headers, data=data)
        print("Status code:", response.status_code)
        try:
            print("JSON response:", response.json())
            return response.json()
        except ValueError:
            print("Raw response:", response.text)
            return None
