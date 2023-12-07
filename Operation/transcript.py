import json

from LoginSession import LoginSession


class Transcript:
    def __init__(self, login_session: LoginSession, query: str = None):
        self.login_session = login_session
        self.data = None
        self.public_courses = None
        self.required_courses = None
        self.url = self.login_session.post(
            "https://pass.hust.edu.cn/cas/login?service=https://cjd.hust.edu.cn/bks/",
            allow_redirects=False,
        ).headers["Location"]
        self.query = query
        self.get_data()
        self.initialize_courses()

    def get_data(self):
        res = self.login_session.get(
            "https://cjd.hust.edu.cn/cas/client/validateLogin"
            + self.url[self.url.find("?"):]
            + "&service=https://cjd.hust.edu.cn/bks/"
        )
        self.login_session.cookies.set("X-Access-Token", res.json()["result"]["token"])
        self.login_session.headers["X-Access-Token"] = res.json()["result"]["token"]
        res = self.login_session.get(
            "https://cjd.hust.edu.cn/student/user/course_info?pageNo=1&pageSize=100&sort=create_time&order=desc"
        ).text
        self.data = json.loads(res)

    def initialize_courses(self):
        courses = self.data["result"]["score"]["records"]
        self.required_courses = {}
        self.public_courses = {}
        for course in courses:
            if course["courseNature"] == "必修":
                self.required_courses[course["courseCname"]] = (course["scoreText"], float(course["credit"]))
            else:
                self.public_courses[course["courseCname"]] = (course["scoreText"], float(course["credit"]))

    def run(self) -> dict:
        if self.query is not None:
            return (
                self.required_courses.get(self.query,
                                          self.public_courses.get(self.query, "课程名称错误"))
            )
        else:
            self.required_courses.update(self.public_courses)
            return self.required_courses
