import re
import time

from LoginSession1 import LoginSession
from Operation.Badminton import Badminton
from Operation.Course import Course
from Operation.CourseAttack import CourseAttack
from Operation.Transcript import Transcript


class operator:
    def __init__(self, loginSession: LoginSession):
        self.userId = None
        self.loginSession = loginSession

    def course(self, course: dict, time: str, function: str = "Attack"):
        course = CourseAttack(self.loginSession, self.userId, course, function)
        course.run(time)

    def transcript(self, query: str = None):
        transcript = Transcript(self.loginSession, query)
        res = transcript.run()
        return res

    def Schedule(self):
        return Course(self.loginSession).Courses

    def badminton(self, partner: list, Date: str, start_time=None, cd: int = 1):
        badminton = Badminton(self.loginSession, partner, Date, start_time, cd)
        return badminton.run()

    def xyk(self, val, password):
        res = self.loginSession.get("http://ecard.m.hust.edu.cn/wechat-web/ChZhController/ChongZhiurl.html")
        cardno = re.search('id="cardno" value="(.*)"/>', res.text).group(1)
        res = self.loginSession.post("http://ecard.m.hust.edu.cn/wechat-web/ChZhController/ChongZhi.html", data={
            "jsoncallback": "jsonp" + str(int(time.time() * 1000)),
            "value": str(val) + "," + str(password),
            "cardno": cardno,
            "acctype": "1"
        })
        return re.search('"errmsg":"(.*?)"', res.text).group(1)
