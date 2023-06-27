import json

from LoginSession import LoginSession


class Transcript:
    def __init__(self, loginSession: LoginSession, query: str = None):
        super().__init__()
        self.loginSession = loginSession
        self.data = None
        self.publicSets = None
        self.mustSets = None
        self.url = self.loginSession.post("https://pass.hust.edu.cn/cas/login?service=https://cjd.hust.edu.cn/bks/",
                                          allow_redirects=False).headers['Location']
        self.query = query
        self.get_data()
        self.init()

    def get_data(self):
        res = self.loginSession.get("https://cjd.hust.edu.cn/cas/client/validateLogin" + self.url[self.url.find(
            '?'):] + "&service=https://cjd.hust.edu.cn/bks/")
        self.loginSession.cookies.set("X-Access-Token", res.json()["result"]["token"])
        self.loginSession.headers["X-Access-Token"] = res.json()["result"]["token"]
        res = self.loginSession.get(
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
