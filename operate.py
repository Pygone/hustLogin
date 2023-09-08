import re
import time

from LoginSession import LoginSession
from Operation.Badminton import Badminton
from Operation.Course import Course
from Operation.CourseAttack import CourseAttack
from Operation.Transcript import Transcript
from Operation.professionalCourse import professionalCourse
from Operation.publicCourse import publicCourse


class operator:
    def __init__(self, loginSession: LoginSession, userId: str):
        """

        :param loginSession: 华中大客户端
        :param userId: 用户名
        """
        self.userId = userId
        self.loginSession = loginSession

    def course(self, course: dict, time_: str = "", function: str = "Attack"):
        """
        专业选修课 抢课插件
        :param course: 课程:教师名
        :param time_: 开始选课的时间
        :param function: 可选参数
               Attack 准点抢课
               Rob 后台自动等待退选抢课 ( 由于选课机制更改 已失效)
        :return:
        """
        course = CourseAttack(self.loginSession, self.userId, course, function)
        course.run(time_)

    def transcript(self, query: str = None) -> dict:
        """
        成绩单查询
        :param query: 查询成绩的课程名, 如不设置则返回所有课程
        :return:
        """
        transcript = Transcript(self.loginSession, query)
        res = transcript.run()
        return res

    def Schedule(self):
        """
        课程表数据查询
        :return: 返回个人的课程表数据 json格式
        """
        return Course(self.loginSession).Courses

    def badminton(self, Date: str, start_time, cd: int = 1, partner: list = None) -> str:
        """
        羽毛球场预约
        :param Date: 预约的日期
        :param start_time: 预约场地的时间段开始节点 %H: 08-20( 指8点场 - 20点场)
        :param cd: 场地号 1-22
        :param partner: 同伴(可选) 不填则自动选择之前注册过的第一个同伴
        :return:
        """
        if partner is None:
            badminton = Badminton(self.loginSession, Date, start_time, cd)
        else:
            badminton = Badminton(self.loginSession, Date, start_time, cd, partner)
        return badminton.run()

    def school_card(self, val: int, password: str) -> str:
        """
        校园卡充值
        :param val: 充值的余额
        :param password: 校园卡密码
        :return: 充值反馈信息
        """
        res = self.loginSession.get(
            "http://ecard.m.hust.edu.cn/wechat-web/ChZhController/ChongZhiurl.html"
        )
        cardno = re.search('id="cardno" value="(.*)"/>', res.text).group(1)
        res = self.loginSession.post(
            "http://ecard.m.hust.edu.cn/wechat-web/ChZhController/ChongZhi.html",
            data={
                "jsoncallback": "jsonp" + str(int(time.time() * 1000)),
                "value": str(val) + "," + str(password),
                "cardno": cardno,
                "acctype": "1",
            },
        )
        return re.search('"errmsg":"(.*?)"', res.text).group(1)

    def professional_course(self):
        return professionalCourse(self.loginSession)

    def public_course(self, query: list):
        worker = publicCourse(self.loginSession, query)
        worker.run()
