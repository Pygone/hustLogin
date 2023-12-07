import datetime
import json
import re
import time

from bs4 import BeautifulSoup

from LoginSession import LoginSession


class Badminton:
    def __init__(self, login_session: LoginSession, date: str, start_time: str, court: int = 1, partner: list = None):
        self.token_2 = None
        self.cg_csrf_token = None
        self.court = str(court)
        self.start_time = datetime.datetime.strptime(start_time, "%H").strftime("%H:%M:%S")
        self.date = date
        self.login_session = login_session
        self.partners = None
        self.partner = partner

    def ecard(self):
        url = "http://ecard.m.hust.edu.cn/wechat-web/service/new_profile.html"
        res = self.login_session.get(url)
        soup = BeautifulSoup(res.text, features="html.parser")
        bills = float(soup.section.find_all("dl")[9].dd.div.span.string.strip("元"))
        return bills < 40 if self.start_time >= "18:00:00" else bills < 20

    def get_partner(self, text):
        params = {
            "id": "0",
            "member_id": "56558",
            "partner_name": "",
            "partner_type": "1",
            "partner_schoolno": "",
            "partner_passwd": "",
            "cg_csrf_token": self.cg_csrf_token,
        }
        if self.partner is None:
            self.partners = re.findall("putPartner\('(.*)','(.*)','(.*)','1'\);", text)
            for partner in self.partners:
                if partner[2] != self.login_session.userId:
                    params["partner_name"] = partner[1]
                    params["partner_schoolno"] = partner[2]
                    params["partner_passwd"] = partner[0]
                    text_ = self.login_session.post("http://pecg.hust.edu.cn/cggl/front/addPartner", data=params).text
                    info = re.search(r"alert\(HTMLDecode\('(.*)'\), '提示信息'\);", text_).group(1)
                    if "你已添加该同伴，请勿重复添加" in info:
                        self.partner = partner
                        break

    def run(self) -> str:
        if self.ecard():
            return "电子账户余额不足"
        self.court = json.load(open("src/court.json"))[self.court]
        date = datetime.datetime.strptime(self.date, "%Y-%m-%d")
        yesterday = date - datetime.timedelta(days=1)
        end_time = (datetime.datetime.strptime(self.start_time, "%H:%M:%S") + datetime.timedelta(hours=2)).strftime(
            "%H:%M:%S")
        self.login_session.headers["Referer"] = self.login_session.get("http://pecg.hust.edu.cn/cggl/index1").url
        url = f"http://pecg.hust.edu.cn/cggl/front/syqk?date={yesterday.strftime('%Y-%m-%d')}&type=1&cdbh=45"
        text = self.login_session.get(url).text
        self.cg_csrf_token = re.search('name="cg_csrf_token" value="(.*)" />', text).group(1)
        self.get_partner(text)
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
        date = str(datetime.datetime.strptime(self.date + " 08", "%Y-%m-%d %H") - datetime.timedelta(days=2))
        date = time.mktime(time.strptime(date, "%Y-%m-%d %H:%M:%S"))
        while time.time() - date < 0:
            time.sleep(1)
        text = self.login_session.post("http://pecg.hust.edu.cn/cggl/front/step2", data=params).text
        try:
            data = re.search('name="data" value="(.*)" type', text).group(1)
            Id = re.search('name="id" value="(.*)" type', text).group(1)
            params = [
                ("data", data),
                ("id", Id),
                ("cg_csrf_token", self.cg_csrf_token),
                ("select_pay_type", -1),
            ]
            text = self.login_session.post("http://pecg.hust.edu.cn/cggl/front/step3", data=params).text
        except AttributeError:
            return re.search(r"alert\(HTMLDecode\('(.*)'\), '提示信息'\);", text).group(1)
        return re.search(r"alert\(HTMLDecode\('(.*)'\), '提示信息'\);", text).group(1)
