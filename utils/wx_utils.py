import time

import requests
from django.conf import settings
from cryptography.fernet import Fernet

from app.models import SessionInfo

url = settings.WX_APP_URL
app_id = settings.WX_APP_ID
app_secret = settings.WX_APP_SECRET


def get_wx_auth_session(code):
    params = {'appid': app_id, 'secret': app_secret, 'js_code': code, 'grant_type': 'authorization_code'}
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            if data.get('errcode', 0) == 0:
                return data
            else:
                return {}
        else:
            return {}
    except Exception as e:
        print(e)
        return {}


class Wx3rdSession:

    def __init__(self, session_key=None, openid=None):
        self.openid = openid
        self.session_key = session_key

    def get_3rd_session(self):
        key = Fernet.generate_key()
        self.save(key)
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(self.openid.encode('utf-8'))
        return encrypted_data

    def get_openid_from_session(self, encrypted_data):
        key = self.get_key()
        cipher = Fernet(key)
        raw_data = cipher.decrypt(encrypted_data)
        return raw_data

    def get_key(self):
        session_info = SessionInfo.objects.filter(self.openid).first()
        return session_info.key

    def save(self, key):
        session_info = SessionInfo(
            openid=self.openid,
            session_key=self.session_key,
            key=key)
        session_info.save()
