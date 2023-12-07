import re

from bs4 import BeautifulSoup

from LoginSession import LoginSession


class Course:
    def __init__(self, login_session: LoginSession):
        self.login_session = login_session
        self.courses = {}
        self.populate_courses()

    def add_course(self, text: str):
        lines = text.split("\n")
        course_name = lines[0]
        teacher_name = lines[2]
        schedule = {"周次": [], "星期": [], "节次": [], "地点": []}
        for idx in range(10, len(lines), 4):
            for i, key in enumerate(schedule.keys()):
                schedule[key].append(lines[idx + i])
        self.courses[course_name] = {"teacherName": teacher_name, "schedule": schedule}

    def populate_courses(self):
        res = self.login_session.get("http://hub.m.hust.edu.cn/kcb/todate/namecourse.action?kcname=&lsname=")
        soup = BeautifulSoup(res.text, features="html.parser")
        for i in soup.find_all("li"):
            text = re.sub("\r|\t", "", i.text).strip().replace(" ", "").replace("\n+", "\n")
            temp = re.search("人数/容量：(.*)\n开课对象", text, re.DOTALL).group(1)
            text = text.replace(temp, temp.replace("\n", ""))
            self.add_course(text)

    def get_courses(self):
        return self.courses
