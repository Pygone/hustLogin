import re
import time

from LoginSession import LoginSession
from Operation.badminton import Badminton
from Operation.course import Course
from Operation.courseRobbing import CourseRobbing
from Operation.professionalCourse import ProfessionalCourse
from Operation.publicCourse import PublicCourse
from Operation.transcript import Transcript


class Operator:
    def __init__(self, login_session: LoginSession, user_id: str):
        self.user_id = user_id
        self.login_session = login_session

    def course(self, course: dict, time_: str = "", function: str = "Attack"):
        course = CourseRobbing(self.login_session, self.user_id, course, function)
        course.run(time_)

    def transcript(self, query: str = None) -> dict:
        transcript = Transcript(self.login_session, query)
        return transcript.run()

    def get_schedule(self):
        return Course(self.login_session).get_courses()

    def badminton(self, date: str, start_time: str, cd: int = 1, partner: list = None) -> str:
        badminton = Badminton(self.login_session, date, start_time, cd, partner)
        return badminton.run()

    def school_card(self, val: int, password: str) -> str:
        res = self.login_session.get("http://ecard.m.hust.edu.cn/wechat-web/ChZhController/ChongZhiurl.html")
        cardno = re.search('id="cardno" value="(.*)"/>', res.text).group(1)
        res = self.login_session.post(
            "http://ecard.m.hust.edu.cn/wechat-web/ChZhController/ChongZhi.html",
            data={
                "jsoncallback": "jsonp" + str(int(time.time() * 1000)),
                "value": str(val) + "," + str(password),
                "cardno": cardno,
                "acctype": "1",
            },
        )
        return re.search('"errmsg":"(.*?)"', res.text).group(1)

    def professional_credit(self):
        return ProfessionalCourse(self.login_session)

    def public_course(self, query: list):
        worker = PublicCourse(self.login_session, query)
        worker.run()