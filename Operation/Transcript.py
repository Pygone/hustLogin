import json

import fake_useragent
import requests
from requests.structures import CaseInsensitiveDict


class Transcript(requests.Session):
    def __init__(self, url, query: str = None):
        super().__init__()
        self.data = None
        self.publicSets = None
        self.mustSets = None
        self.url = url
        self.query = query
        self.get_data()
        self.init()

    def get_data(self):
        self.headers = CaseInsensitiveDict({"User-Agent": fake_useragent.UserAgent().chrome})
        self.get(self.url)
        res = self.get("https://cjd.hust.edu.cn/cas/client/validateLogin" + self.url[self.url.find(
            '?'):] + "&service=https://cjd.hust.edu.cn/bks/")
        self.cookies.set("X-Access-Token", res.json()["result"]["token"])
        self.headers["X-Access-Token"] = res.json()["result"]["token"]
        res = self.get(
            "https://cjd.hust.edu.cn/student/user/course_info?pageNo=1&pageSize=100&sort=create_time&order=desc").text
        self.data = json.loads(res)

    def init(self):
        sets = self.data["result"]["score"]["records"]
        self.mustSets = {}
        self.publicSets = {}
        for i in sets:
            if i['courseNature'] == '必修':
                self.mustSets[i['courseCname']] = (i['scoreText'], float(i['credit']))
            else:
                self.publicSets[i['courseCname']] = (i['scoreText'], float(i['credit']))

    def run(self):
        if self.query is not None:
            return self.mustSets[self.query] if self.query in self.mustSets.keys() else self.publicSets[self.query]
        else:
            self.mustSets.update(self.publicSets)
            return self.mustSets
