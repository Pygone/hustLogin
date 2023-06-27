import re
from random import random

import fake_useragent
import requests
from requests.structures import CaseInsensitiveDict

from util import captcha
from util.rsaEncoder import rsaEncoder

user_agent = fake_useragent.UserAgent().chrome


class LoginSession(requests.Session):
    def __init__(self, userId, password):
        super().__init__()
        self.code = None
        self.url = "https://one.hust.edu.cn/dcp/"
        self.RSApassword = None
        self.RSAuserId = None
        self.rsa = None
        self.lt = None
        self.password = password
        self.userId = userId
        self.headers = CaseInsensitiveDict({"User-Agent": user_agent})
        self.Login()

    def get_code(self):
        captchaContent = self.get("https://pass.hust.edu.cn/cas/code?" + str(random()), stream=True)
        captchaContent.raw.decode_content = True
        self.code = captcha.deCaptcha(captchaContent.raw)

    def get_rsa(self):
        rsa = self.post("https://pass.hust.edu.cn/cas/rsa").json()
        self.rsa = rsa['publicKey']
        self.RSAuserId, self.RSApassword = rsaEncoder(self.userId, self.password, self.rsa).encode()

    def get_lt(self):
        res = self.get(self.url)
        self.lt = re.search(
            '<input type="hidden" id="lt" name="lt" value="(.*)" />', res.text
        ).group(1)

    def Login(self):
        try:
            self.get_lt()
            self.get_code()
            self.get_rsa()
            post_params = {
                "code": self.code,
                "rsa": "",
                "ul": self.RSAuserId,
                "pl": self.RSApassword,
                "lt": self.lt,
                "execution": "e1s1",
                "_eventId": "submit",
            }
            self.post(
                "https://pass.hust.edu.cn/cas/login?service=http://one.hust.edu.cn/dcp/index.jsp", data=post_params
            )
        except:
            self.Login()
