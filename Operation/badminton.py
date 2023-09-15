import datetime
import json
import logging
import re
import time

import fake_useragent
from bs4 import BeautifulSoup

from LoginSession import LoginSession

user_agent = fake_useragent.UserAgent().chrome


class Badminton:
    def __init__(
            self,
            loginSession: LoginSession,
            Date: str,
            start_time: str,
            court: int = 1,
            partner: list = None,
    ):
        super().__init__()
        self.token_2 = None
        self.cg_csrf_token = None
        self.court = str(court)
        s = datetime.datetime.strptime(start_time, "%H")
        self.start_time = s.strftime("%H:%M:%S")
        self.Date = Date
        self.loginSession = loginSession
        self.partners = None
        if partner is not None:
            self.partner = partner
        else:
            self.partner = None

    def ecard(self):
        url = "http://ecard.m.hust.edu.cn/wechat-web/service/new_profile.html"
        res = self.loginSession.get(url)
        soup = BeautifulSoup(res.text, features="html.parser")
        bills = float(soup.section.find_all("dl")[9].dd.div.span.string.strip("元"))
        if bills < 40 and self.start_time >= "18:00:00":
            return True
        if bills < 20 and self.start_time < "18:00:00":
            return True
        return False

    def getPartner(self, text):
        params = {
            "id": "0",
            "member_id": "56558",
            "partner_name": "",
            "partner_type": "1",
            "partner_schoolno": "",
            "partner_passwd": "",
            "cg_csrf_token": self.cg_csrf_token,
            "token": self.token_2
        }
        if self.partner is None:
            self.partners = re.findall(
                "putPartner\('(.*)','(.*)','(.*)','(.*)'\);", text
            )
            if len(self.partners) == 0:
                return "您的账户未绑定同伴"
            for partner in self.partners:
                if partner[2] == self.loginSession.userId:
                    return "不可将自己设置为同伴"
                params["partner_name"] = partner[1]
                params["partner_schoolno"] = partner[2]
                params["partner_passwd"] = partner[0]
                text_ = self.loginSession.post("http://pecg.hust.edu.cn/cggl/front/addPartner", data=params).text
                info = re.search(r"alert\(HTMLDecode\('(.*)'\), '提示信息'\);", text_).group(1)
                if "你已添加该同伴，请勿重复添加" in info:
                    self.partner = partner
                    break
            if self.partner is None:
                return "您的账户绑定的同伴均为无效账户, 可能该用户密码已修改"

    def run(self) -> str:
        # if self.ecard():
        #     return "电子账户余额不足"
        self.court = json.load(open("src/court.json"))[self.court]
        date = datetime.datetime.strptime(self.Date, "%Y-%m-%d")
        yesterday = date - datetime.timedelta(days=1)
        end_time = (datetime.datetime.strptime(
            self.start_time, "%H:%M:%S"
        ) + datetime.timedelta(hours=2)).strftime("%H:%M:%S")
        self.loginSession.headers["Referer"] = self.loginSession.get("http://pecg.hust.edu.cn/cggl/index1").url
        url = f"http://pecg.hust.edu.cn/cggl/front/syqk?date={yesterday.strftime('%Y-%m-%d')}&type=1&cdbh=45"
        text = self.loginSession.get(url).text
        self.cg_csrf_token = re.search(
            'name="cg_csrf_token" value="(.*)" />', text
        ).group(1)
        self.getPartner(text)
        params = [
            ("starttime", self.start_time),
            ("endtime", end_time),
            ("partnerCardType", "1"),
            ("partnerName", self.partner[1]),
            ("partnerSchoolNo", self.partner[2]),
            ("partnerPwd", self.partner[0]),
            ("choosetime", self.court),
            ("changdibh", "45"),
            ("date", date.strftime("%Y-%m-%d")),
            ("cg_csrf_token", self.cg_csrf_token),
        ]
        date = datetime.datetime.strptime(
            self.Date + " 08", "%Y-%m-%d %H"
        ) - datetime.timedelta(days=2)
        while True:
            diff = datetime.datetime.now() - date
            diff = diff.days * 86400 + diff.seconds
            if diff >= 0:
                break
            else:
                logging.info(f"等待中, 剩余{-diff}secs 开始")
                if -diff > 3:
                    time.sleep(-diff - 3)
                else:
                    time.sleep(0.05)
                continue
        text = self.loginSession.post("http://pecg.hust.edu.cn/cggl/front/step2", data=params).text
        try:
            data = re.search('name="data" value="(.*)" type', text).group(1)
            Id = re.search('name="id" value="(.*)" type', text).group(1)
            params = [
                ("data", data),
                ("id", Id),
                ("cg_csrf_token", self.cg_csrf_token),
                ("select_pay_type", -1),
            ]
            text = self.loginSession.post("http://pecg.hust.edu.cn/cggl/front/step3", data=params).text
        except AttributeError:
            return re.search(r"alert\(HTMLDecode\('(.*)'\), '提示信息'\);", text).group(1)
        return re.search(r"alert\(HTMLDecode\('(.*)'\), '提示信息'\);", text).group(1)
