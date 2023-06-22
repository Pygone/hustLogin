import json
import re
import time
from random import random

import fake_useragent
import requests
from requests.structures import CaseInsensitiveDict

from Operation.Badminton import Badminton
from Operation.Course import Course
from Operation.CourseAttack import CourseAttack
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
        rsa = self.post("https://pass.hust.edu.cn/cas/rsa").json()
        self.rsa = rsa['publicKey']
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
            return self.__operate(operation)
        return url

    def course(self, course: dict, time: str, function: str = "Attack"):
        course = CourseAttack(self.__operate("wsxk"), self.userId, course, function)
        course.run(time)

    def transcript(self, query: str = None):
        transcript = Transcript(self.__operate("cjd"), query)
        res = transcript.run()
        return res

    def Schedule(self):
        return Course(self.__operate("kb")).Courses

    def badminton(self, partner: list, Date: str, start_time=None, cd: int = 1):
        badminton = Badminton(self.__operate("badminton"), partner, Date, start_time, cd)
        return badminton.run()

    def xyk(self, val, password):
        url = self.__operate("xyk")
        with requests.session() as session:
            session.get(url)
            res = session.get("http://ecard.m.hust.edu.cn/wechat-web/ChZhController/ChongZhiurl.html")
            cardno = re.search('id="cardno" value="(.*)"/>', res.text).group(1)
            res = session.post("http://ecard.m.hust.edu.cn/wechat-web/ChZhController/ChongZhi.html", data={
                "jsoncallback": "jsonp" + str(int(time.time() * 1000)),
                "value": str(val) + "," + str(password),
                "cardno": 279760,
                "acctype": "1"
            })
            return re.search('"errmsg":"(.*?)"', res.text).group(1)
