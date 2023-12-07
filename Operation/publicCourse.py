import re
import time

from bs4 import BeautifulSoup

from LoginSession import LoginSession


class PublicCourse:
    def __init__(self, login_session: LoginSession, query: list):
        self.login_session = login_session
        self.query = query
        self.valid_courses = []

    def get_all_course_params(self, course_id):
        response = self.login_session.post(
            "http://wsxk.hust.edu.cn/zxqstudentcourse/zxqclassroom.action",
            data={"markZB": "", "ggkdll": "", "kcbh": course_id},
        )
        course_ids = re.findall("ClassWhenWhereForZxq\('(.*)','.*'\)", response.text)
        rooms = re.findall("selectKT\(this.id,'(.*)','(.*)'\);", response.text)
        course_params = [i["value"] for i in
                         BeautifulSoup(response.text, features="html.parser").table.find_all("tr")[1].form.find_all(
                             "input")]
        for i in range(len(rooms)):
            course_params_dict = dict(zip(["ktbh", "ktrl", "ktrs"], [course_ids[i], *rooms[i]]))
            self.valid_courses.append({**dict(zip(course_params[::2], course_params[1::2])), **course_params_dict})

    def check_course_conflict(self):
        for course in self.valid_courses.copy():
            response = self.login_session.post(
                "http://wsxk.hust.edu.cn/zxqstudentcourse/zxqcoursesresult.action",
                data=course,
            )
            msg = BeautifulSoup(response.text, features="html.parser").body.div.find_all("div")[1].ul.li.string.strip()
            if "冲突" in msg or "已经选修该公共任选课，不能够再选修该公共任选课" in msg or "选课失败，课堂人数已满！" not in msg:
                self.valid_courses.remove(course)

    def run(self):
        self.login_session.get("http://wsxk.hust.edu.cn/hustpass2.action")
        time.sleep(0.5)
        self.login_session.get("http://wsxk.hust.edu.cn/studentControl!chooseSystem.action?xkxt=zxq")
        for course in self.query:
            response = self.login_session.post(
                "http://wsxk.hust.edu.cn/zxqstudentcourse/zxqcourses.action",
                data={"markZB": "", "ggkdll": "", "GGKDLBH": "0", "kcmc": course},
            )
            course_id = re.search("onclick=\"selectKT\(this.id,'(.*)'\)", response.text).group(1)
            self.get_all_course_params(course_id)
        self.check_course_conflict()
        while self.valid_courses:
            for course in self.valid_courses.copy():
                response = self.login_session.post(
                    "http://wsxk.hust.edu.cn/zxqstudentcourse/zxqcoursesresult.action",
                    data=course,
                )
                msg = BeautifulSoup(response.text, features="html.parser").body.div.find_all("div")[
                    1].ul.li.string.strip()
                if "选课失败，课堂人数已满！" not in msg:
                    self.valid_courses.remove(course)
