import random
import re
import time

from bs4 import BeautifulSoup

from LoginSession import LoginSession
from Operation.Badminton import Badminton
from Operation.Course import Course
from Operation.CourseAttack import CourseAttack
from Operation.Transcript import Transcript


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

    def transcript(self, query: str = None):
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

    def badminton(self, Date: str, start_time, cd: int = 1, partner: list = None):
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

    def school_card(self, val, password):
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
        self.loginSession.get("http://hubs.hust.edu.cn/hustpass.action")
        res = self.loginSession.post(
            "http://hubs.hust.edu.cn/plan/Plan_queryPlanModuleCourse.action",
            data={"nj": "2021", "zybh": "004068", "mkid": "2708"},
        )
        course_credit = {}
        for i in res.json()["data"]:
            course_credit[i["KCMC"]] = []
            course_credit[i["KCMC"]].append(i["KCZXF"])
            temp = self.loginSession.post(
                "http://hubs.hust.edu.cn/plan/Plan_queryXdbj.action",
                data={"kcbh": i["KCBH"]},
            )
            course_credit[i["KCMC"]].append(temp.json()["result"])
        sum_credit = 0
        for i in course_credit.values():
            if i[1]:
                sum_credit += i[0]
        print(sum_credit)

    def public_course(self, query: list):
        valid_list = list()

        def get_all_courseParams(course_id):
            res_ = self.loginSession.post(
                "http://wsxk.hust.edu.cn/zxqstudentcourse/zxqclassroom.action",
                data={"markZB": "", "ggkdll": "", "kcbh": course_id},
            )
            soup = BeautifulSoup(res_.text, features="html.parser")
            course_ids = re.findall("ClassWhenWhereForZxq\('(.*)','.*'\)", res_.text)
            rooms = re.findall("selectKT\(this.id,'(.*)','(.*)'\);", res_.text)
            res_list2 = soup.table.find_all("tr")[1].form.find_all("input")
            res_dict = {}
            for i in res_list2:
                res_dict[i["name"]] = i["value"]
            for i in range(len(rooms)):
                res_dict["ktbh"] = course_ids[i]
                res_dict["ktrl"] = rooms[i][0]
                res_dict["ktrs"] = rooms[i][1]
                valid_list.append(res_dict.copy())

        def test_if_conflict():
            validList = valid_list.copy()
            for course_dict_ in validList:
                res_ = self.loginSession.post(
                    "http://wsxk.hust.edu.cn/zxqstudentcourse/zxqcoursesresult.action",
                    data=course_dict_,
                )
                soup = BeautifulSoup(res_.text, features="html.parser")
                try:
                    msg = soup.body.div.find_all("div")[1].ul.li.string.strip()
                    if "冲突" in msg:
                        print(course_dict_["kcmc"], "选课时间冲突")
                        valid_list.remove(course_dict_)
                    elif "已经选修该公共任选课，不能够再选修该公共任选课" in msg:
                        print("您已选修该课程", course_dict_["kcmc"])
                        valid_list.remove(course_dict_)
                    elif "选课失败，课堂人数已满！" in msg:
                        continue
                    else:
                        print(msg)
                        valid_list.remove(course_dict_)
                except:
                    print("存在冲突")
                    valid_list.remove(course_dict_)

        self.loginSession.get("http://wsxk.hust.edu.cn/hustpass2.action")
        time.sleep(0.5)
        self.loginSession.get(
            "http://wsxk.hust.edu.cn/studentControl!chooseSystem.action?xkxt=zxq"
        )
        for course in query:
            res = self.loginSession.post(
                "http://wsxk.hust.edu.cn/zxqstudentcourse/zxqcourses.action",
                data={"markZB": "", "ggkdll": "", "GGKDLBH": "0", "kcmc": course},
            )
            course_id = re.search("onclick=\"selectKT\(this.id,'(.*)'\)", res.text).group(1)
            get_all_courseParams(course_id)
        test_if_conflict()
        while True:
            ValList = valid_list.copy()
            if len(valid_list) == 0:
                break
            for course_dict in ValList:
                if course_dict["ktrs"] < course_dict["ktrl"]:
                    self.loginSession.post(
                        "http://wsxk.hust.edu.cn/zxqstudentcourse/zxqcoursesresult.action",
                        data=course_dict,
                    )
                    valid_list.remove(course_dict)
                    continue
                else:
                    print(course_dict["kcmc"], "full, keep waiting")
            time.sleep(random.randint(5, 8))
