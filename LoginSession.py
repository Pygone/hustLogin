import json
import re
from random import random

import fake_useragent
import requests
from requests.structures import CaseInsensitiveDict

from Operation.Course import Course
from Operation.Transcript import Transcript
from util import captcha
from util.rsaEncoder import rsaEncoder

user_agent = fake_useragent.UserAgent().chrome


class LoginSession(requests.Session):
    def __init__(self, userId, password):
        super().__init__()
        self.code = None
        self.url = None
        self.RSApassword = None
        self.RSAuserId = None
        self.rsa = None
        self.lt = None
        self.password = password
        self.userId = userId
        self.headers = CaseInsensitiveDict({"User-Agent": user_agent})

    def get_code(self):
        captchaContent = self.get("https://pass.hust.edu.cn/cas/code?" + str(random()), stream=True)
        captchaContent.raw.decode_content = True
        self.code = captcha.deCaptcha(captchaContent.raw)

    def get_rsa(self):
        rsa = self.post("https://pass.hust.edu.cn/cas/rsa").text
        self.rsa = json.loads(rsa)['publicKey']
        self.RSAuserId, self.RSApassword = rsaEncoder(self.userId, self.password, self.rsa).encode()

    def get_lt(self):
        res = self.get(self.url)
        self.lt = re.search(
            '<input type="hidden" id="lt" name="lt" value="(.*)" />', res.text
        ).group(1)

    def getDirection(self, operation):
        self.url = "https://pass.hust.edu.cn/cas/login?service=" + json.load(open("src/operation.json"))[operation]
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
        redirect_html = self.post(
            self.url, data=post_params, allow_redirects=False
        )
        return redirect_html.headers["Location"]

    def __operate(self, operation):
        try:
            url = self.getDirection(operation)
        except:
            self.headers = CaseInsensitiveDict({"User-Agent": user_agent})
            self.cookies.clear()
            return self.options(operation)
        if operation == "wsxk":
            return url
        if operation == "cjd":
            with requests.session() as Session:
                Session.headers = CaseInsensitiveDict({"User-Agent": fake_useragent.UserAgent().chrome})
                Session.get(url)
                res = Session.get("https://cjd.hust.edu.cn/cas/client/validateLogin" + url[url.find(
                    '?'):] + "&service=https://cjd.hust.edu.cn/bks/")
                Session.cookies.set("X-Access-Token", res.json()["result"]["token"])
                Session.headers["X-Access-Token"] = res.json()["result"]["token"]
                res = Session.get(
                    "https://cjd.hust.edu.cn/student/user/course_info?pageNo=1&pageSize=100&sort=create_time&order=desc").text
                data = json.loads(res)
                return data

    def course(self, course: dict, time: str, function: str = "Attack"):
        course = Course(self.__operate("wsxk"), self.userId, course, function)
        course.run(time)

    def transcript(self, query: str = None):
        transcript = Transcript(self.__operate("cjd"), query)
        res = transcript.run()
        return res
