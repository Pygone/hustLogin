import re
import time
from random import random

import fake_useragent
import requests
from requests.structures import CaseInsensitiveDict

from util import captcha
from util.rsaEncoder import RsaEncoder

user_agent = fake_useragent.UserAgent().chrome


class LoginSession(requests.Session):
    def __init__(self, userId, password):
        super().__init__()
        self.url = "https://one.hust.edu.cn/dcp/"
        self.password = password
        self.userId = userId
        self.headers = CaseInsensitiveDict({"User-Agent": user_agent})
        self.Login()

    def get_code(self):
        captchaContent = self.get("https://pass.hust.edu.cn/cas/code?" + str(random()), stream=True)
        captchaContent.raw.decode_content = True
        return captcha.deCaptcha(captchaContent.raw)

    def get_rsa(self):
        rsa = self.post("https://pass.hust.edu.cn/cas/rsa").json()
        return RsaEncoder(self.userId, self.password, rsa['publicKey']).encode()

    def get_lt(self):
        res = self.get(self.url)
        return re.search('<input type="hidden" id="lt" name="lt" value="(.*)" />', res.text).group(1)

    def Login(self):
        cnt = 0
        try:
            lt = self.get_lt()
            code = self.get_code()
            rsa_userId, rsa_password = self.get_rsa()
            post_params = {
                "code": code,
                "rsa": "",
                "ul": rsa_userId,
                "pl": rsa_password,
                "lt": lt,
                "execution": "e1s1",
                "_eventId": "submit",
            }
            self.post("https://pass.hust.edu.cn/cas/login?service=http://one.hust.edu.cn/dcp/index.jsp",
                      data=post_params)
            print("Login success!")
        except:
            time.sleep(5)
            cnt += 1
            print("Login failed, retrying...", cnt)
            self.Login()
