import datetime
import json
import os
import re
import time

import fake_useragent
import requests
from requests.structures import CaseInsensitiveDict


user_agent = fake_useragent.UserAgent().chrome


class Badminton(requests.Session):
    def __init__(self, url, partner: list, Date: str, start_time=None, cd: int = 1):
        super().__init__()
        self.headers = CaseInsensitiveDict({
            "User-Agent": user_agent})
        self.cd = cd
        self.start_time = start_time
        self.Date = Date
        self.partner = partner
        self.url = url

    def run(self):
        Cd = json.load(open("src/court.json"))
        date = datetime.datetime.strptime(self.Date, "%Y-%m-%d")
        yesterday = date - datetime.timedelta(days=1)
        end_time = datetime.datetime.strptime(self.start_time, "%H:%M:%S") + datetime.timedelta(hours=2)
        end_time = end_time.strftime("%H:%M:%S")
        url = self.get(self.url).url
        self.headers["Referer"] = url
        url = f"http://pecg.hust.edu.cn/cggl/front/syqk?date={yesterday.strftime('%Y-%m-%d')}&type=1&cdbh=45"
        res = self.get(url)
        cg_csrf_token = re.search('name="cg_csrf_token" value="(.*)" />', res.text).group(1)
        token_1 = re.search(r'name=\\"token\\" value=\\"(.*)\\" >"', res.text).group(1)
        params = {"changdibh": "45",
                  "data": "110@08:00:00-10:00:00,133@08:00:00-10:00:00,215@08:00:00-10:00:00,216@08:00:00-10:00:00,218@08:00:00-10:00:00,376@08:00:00-10:00:00,217@08:00:00-10:00:00,219@08:00:00-10:00:00,220@08:00:00-10:00:00,221@08:00:00-10:00:00,222@08:00:00-10:00:00,223@08:00:00-10:00:00,224@08:00:00-10:00:00,368@08:00:00-10:00:00,369@08:00:00-10:00:00,370@08:00:00-10:00:00,377@08:00:00-10:00:00,371@08:00:00-10:00:00,372@08:00:00-10:00:00,373@08:00:00-10:00:00,374@08:00:00-10:00:00,375@08:00:00-10:00:00,",
                  "date": date.strftime('%Y-%m-%d'),
                  "time": time.strftime('%a %b %d %Y %H:%M:%S GMT+0800 (中国标准时间)', time.localtime()),
                  "token": token_1
                  }
        self.headers[
            "Referer"] = f"http://pecg.hust.edu.cn/cggl/front/syqk?date={yesterday.strftime('%Y-%m-%d')}&type=1&cdbh=45"
        self.headers["X-Requested-With"] = "XMLHttpRequest"
        res = self.post("http://pecg.hust.edu.cn/cggl/front/ajax/getsyzt", data=params).json()
        self.headers.pop("X-Requested-With")
        token_2 = res[0]["token"]
        params = [
            ("starttime", self.start_time),
            ("endtime", end_time),
            ("partnerCardType", "1"),
            ("partnerName", self.partner[0]),
            ("partnerSchoolNo", self.partner[1]),
            ("partnerPwd", self.partner[2]),
            ("choosetime", Cd[str(self.cd)]),
            ("changdibh", "45"),
            ("date", date.strftime('%Y-%m-%d')),
            ("cg_csrf_token", cg_csrf_token),
            ('token', token_2)
        ]
        self.headers[
            "Referer"] = f"http://pecg.hust.edu.cn/cggl/front/syqk?date={yesterday.strftime('%Y-%m-%d')}&type=1&cdbh=45"
        res = self.post("http://pecg.hust.edu.cn/cggl/front/step2", data=params)
        data = re.search('name="data" value="(.*)" type', res.text).group(1)
        Id = re.search('name="id" value="(.*)" type', res.text).group(1)
        params = [
            ("data", data),
            ("id", Id),
            ("cg_csrf_token", cg_csrf_token),
            ("token", token_2)
        ]
        self.headers["Referer"] = "http://pecg.hust.edu.cn/cggl/front/step2"
        res = self.post("http://pecg.hust.edu.cn/cggl/front/step3", data=params)
        return re.search(r"alert\(HTMLDecode\('(.*)'\), '提示信息'\);", res.text).group(1)
