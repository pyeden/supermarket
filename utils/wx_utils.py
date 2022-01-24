import time

import requests
from django.conf import settings
from cryptography.fernet import Fernet
from django.db import connections

from app import models as mo

url = settings.WX_APP_URL
app_id = settings.WX_APP_ID
app_secret = settings.WX_APP_SECRET


def get_key():
    s = mo.SecretKey.objects.first()
    if not s:
        key = Fernet.generate_key().decode('utf-8')
        r = mo.SecretKey.objects.create(key=key)
        r.save()
        return key
    return s.key.encode('utf-8')


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

    def __init__(
            self,
            session_key=None,
            openid=None,
            encrypted_data=None

    ):
        self.openid = openid
        self.session_key = session_key
        self.encrypted_data = encrypted_data
        self.key = get_key()

    @property
    def token(self):
        cipher = Fernet(self.key)
        encrypted_data = cipher.encrypt(self.openid.encode('utf-8'))
        return encrypted_data.decode('utf-8')

    @property
    def open_id(self):
        cipher = Fernet(self.key)
        raw_data = cipher.decrypt(self.encrypted_data.encode('utf-8'))
        return raw_data.decode('utf-8')

    def save_session_info(self):
        info = mo.SessionInfo.objects.filter(openid=self.openid).first()
        if not info:
            mo.SessionInfo.objects.create(
                key=self.key.decode('utf-8'),
                openid=self.openid,
                session_key=self.session_key,
            )


def get_token(openid):
    r = Wx3rdSession(openid=openid)
    return r.token


def get_openid(token):
    r = Wx3rdSession(encrypted_data=token)
    return r.open_id
