import datetime
import json
import logging
import re
import time

import fake_useragent

from LoginSession import LoginSession

user_agent = fake_useragent.UserAgent().chrome


class Badminton:
    def __init__(
            self,
            loginSession: LoginSession,
            Date: str,
            start_time: str,
            cd: int = 1,
            partner: list = None,
    ):
        super().__init__()
        self.cd = cd
        s = datetime.datetime.strptime(start_time, "%H")
        self.start_time = s.strftime("%H:%M:%S")
        self.Date = Date
        self.loginSession = loginSession
        if partner is not None:
            self.partner = partner
        else:
            self.partner = None

    def run(self) -> str:
        Cd = json.load(open("src/court.json"))
        date = datetime.datetime.strptime(self.Date, "%Y-%m-%d")
        yesterday = date - datetime.timedelta(days=1)
        end_time = datetime.datetime.strptime(
            self.start_time, "%H:%M:%S"
        ) + datetime.timedelta(hours=2)
        end_time = end_time.strftime("%H:%M:%S")
        url = self.loginSession.get("http://pecg.hust.edu.cn/cggl/index1").url
        self.loginSession.headers["Referer"] = url
        url = f"http://pecg.hust.edu.cn/cggl/front/syqk?date={yesterday.strftime('%Y-%m-%d')}&type=1&cdbh=45"
        res = self.loginSession.get(url)
        if self.partner is None:
            partners = re.findall(
                "putPartner\('(.*)','(.*)','(.*)','(.*)'\);", res.text
            )
            if len(partners) != 0:
                self.partner = partners[0]
            else:
                return "您的账户未绑定同伴"
        cg_csrf_token = re.search(
            'name="cg_csrf_token" value="(.*)" />', res.text
        ).group(1)
        token_1 = re.search(r'name=\\"token\\" value=\\"(.*)\\" >"', res.text).group(1)
        params = {
            "changdibh": "45",
            "data": "110@08:00:00-10:00:00,133@08:00:00-10:00:00,215@08:00:00-10:00:00,216@08:00:00-10:00:00,"
                    "218@08:00:00-10:00:00,376@08:00:00-10:00:00,217@08:00:00-10:00:00,219@08:00:00-10:00:00,"
                    "220@08:00:00-10:00:00,221@08:00:00-10:00:00,222@08:00:00-10:00:00,223@08:00:00-10:00:00,"
                    "224@08:00:00-10:00:00,368@08:00:00-10:00:00,369@08:00:00-10:00:00,370@08:00:00-10:00:00,"
                    "377@08:00:00-10:00:00,371@08:00:00-10:00:00,372@08:00:00-10:00:00,373@08:00:00-10:00:00,"
                    "374@08:00:00-10:00:00,375@08:00:00-10:00:00,",
            "date": date.strftime("%Y-%m-%d"),
            "time": time.strftime(
                "%a %b %d %Y %H:%M:%S GMT+0800 (中国标准时间)", time.localtime()
            ),
            "token": token_1,
        }
        self.loginSession.headers[
            "Referer"
        ] = f"http://pecg.hust.edu.cn/cggl/front/syqk?date={yesterday.strftime('%Y-%m-%d')}&type=1&cdbh=45"
        self.loginSession.headers["X-Requested-With"] = "XMLHttpRequest"
        res = self.loginSession.post(
            "http://pecg.hust.edu.cn/cggl/front/ajax/getsyzt", data=params
        ).json()
        self.loginSession.headers.pop("X-Requested-With")
        token_2 = res[0]["token"]
        params = [
            ("starttime", self.start_time),
            ("endtime", end_time),
            ("partnerCardType", "1"),
            ("partnerName", self.partner[1]),
            ("partnerSchoolNo", self.partner[2]),
            ("partnerPwd", self.partner[0]),
            ("choosetime", Cd[str(self.cd)]),
            ("changdibh", "45"),
            ("date", date.strftime("%Y-%m-%d")),
            ("cg_csrf_token", cg_csrf_token),
            ("token", token_2),
        ]
        self.loginSession.headers[
            "Referer"
        ] = f"http://pecg.hust.edu.cn/cggl/front/syqk?date={yesterday.strftime('%Y-%m-%d')}&type=1&cdbh=45"
        while True:
            date = datetime.datetime.strptime(
                self.Date + " 08", "%Y-%m-%d %H"
            ) - datetime.timedelta(days=2)
            diff = datetime.datetime.now() - date
            diff = diff.days * 86400 + diff.seconds
            if diff > 0.1:
                break
            else:
                logging.info(f"等待中, 剩余{-diff}secs 开始")
                if -diff > 3:
                    time.sleep(-diff - 3)
                else:
                    time.sleep(0.1)
                continue
        res = self.loginSession.post(
            "http://pecg.hust.edu.cn/cggl/front/step2", data=params
        )
        try:
            data = re.search('name="data" value="(.*)" type', res.text).group(1)
            Id = re.search('name="id" value="(.*)" type', res.text).group(1)
            params = [
                ("data", data),
                ("id", Id),
                ("cg_csrf_token", cg_csrf_token),
                ("token", token_2),
                ("select_pay_type", -1),
            ]
            self.loginSession.headers[
                "Referer"
            ] = "http://pecg.hust.edu.cn/cggl/front/step2"
            res = self.loginSession.post(
                "http://pecg.hust.edu.cn/cggl/front/step3", data=params
            )
        except AttributeError:
            return re.search(r"alert\(HTMLDecode\('(.*)'\), '提示信息'\);", res.text).group(1)
        return re.search(r"alert\(HTMLDecode\('(.*)'\), '提示信息'\);", res.text).group(1)
