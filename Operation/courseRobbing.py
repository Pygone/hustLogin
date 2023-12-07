import asyncio
import logging
import sys
import time
from datetime import datetime

import aiohttp
from requests import JSONDecodeError

from LoginSession import LoginSession

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)


class CourseRobbing:
    def __init__(self, login_session: LoginSession, user_id, course: dict, function: str = "Attack"):
        self.login_session = login_session
        self.function = function
        self.user_id = user_id
        self.course = course
        self.request_list = {}
        self.XQH = None

    def init_(self):
        self.get_course()
        self.muti_get_class_id()

    async def post_method(self, url, data, course, teacher_num):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=data, headers=self.login_session.headers,
                                    cookies=self.login_session.cookies) as response:
                assert response.status == 200
                json = await response.json()
                if json["code"] == "0":
                    logging.info(f"学号为{self.user_id}的同学, 您已抢到{course}:{self.course[course][teacher_num]}")
                else:
                    logging.info(json["msg"])

    async def get_class_id(self, url, data, course):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=data, headers=self.login_session.headers,
                                    cookies=self.login_session.cookies) as response:
                assert response.status == 200
                json = await response.json()
                course_list = {i["KTBH"] for i in json["data"] if i["XM"] in self.course[course]}
                self.request_list[course].append(list(course_list))

    def get_course(self):
        data = {"page": 1, "limit": 10, "fzxkfs": "", "xkgz": 1}
        res = self.login_session.post(url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/getXsFaFZkc", data=data,
                                      allow_redirects=False)
        try:
            res_json = res.json()
        except JSONDecodeError:
            logging.error("Cookie 无效!")
            sys.exit(-1)
        if res_json["count"] == 0:
            logging.error("时间选择有误?")
            sys.exit(-1)
        for i in res_json["data"]:
            for j in self.course.keys():
                if i["KCMC"] == j:
                    ID = i["ID"]
                    KCBH = i["KCBH"]
                    FZID = i["FZID"]
                    self.XQH = i["XQH"]
                    self.request_list[j] = list([ID, KCBH, FZID])

    def muti_get_class_id(self):
        tasks = []
        loop = asyncio.new_event_loop()
        for course in self.course.keys():
            data = {
                "page": 1,
                "limit": 10,
                "fzid": self.request_list[course][2],
                "kcbh": self.request_list[course][1],
                "sfid": self.user_id,
                "faid": self.request_list[course][0],
                "id": self.request_list[course][0],
            }
            tasks.append(loop.create_task(
                self.get_class_id(url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/getFzkt", data=data, course=course)))
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    def muti_post(self):
        tasks = []
        loop = asyncio.new_event_loop()
        for course in self.course.keys():
            for i in range(len(self.request_list[course][3])):
                data = {
                    "ktbh": self.request_list[course][3][i],
                    "xqh": self.XQH,
                    "kcbh": self.request_list[course][1],
                    "fzid": self.request_list[course][2],
                    "faid": self.request_list[course][0],
                    "sfid": self.user_id,
                }
                tasks.append(loop.create_task(
                    self.post_method(url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/addStuxkIsxphx", data=data, course=course,
                                     teacher_num=i)))
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    def rob_class(self):
        while True:
            if len(self.course) == 0:
                sys.exit(1)
            teachers_ = {}
            for course in self.course.keys():
                teachers_[course] = []
                data = {
                    "page": 1,
                    "limit": 10,
                    "fzid": self.request_list[course][2],
                    "kcbh": self.request_list[course][1],
                    "sfid": self.user_id,
                    "faid": self.request_list[course][0],
                    "id": self.request_list[course][0],
                }
                res = self.login_session.post(url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/getFzkt", data=data)
                resjson = res.json()
                for i in resjson["data"]:
                    if i["XM"] in self.course[course] and i["KTRS"] < i["KTRL"]:
                        if i["XM"] not in teachers_[course]:
                            teachers_[course].append(i["XM"])
                        else:
                            continue
                        response = self.login_session.post(
                            url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/addStuxkIsxphx",
                            data={
                                "ktbh": i["KTBH"],
                                "xqh": self.XQH,
                                "kcbh": self.request_list[course][1],
                                "fzid": self.request_list[course][2],
                                "faid": self.request_list[course][0],
                                "sfid": self.user_id,
                            },
                        )
                        json = response.json()
                        if json["code"] == "0":
                            logging.info(f"学号为{self.user_id}的同学, 您已抢到{course}:{i['XM']}")
                            self.course.pop(course)
                            continue
                        elif json["msg"] == "当前学期或之前学期已选该课程，不可重复选择，可在‘选课记录’中查看！":
                            logging.info(json["msg"])
                            self.course.pop(course)
                            continue
                        else:
                            logging.info(json["msg"])
                            sys.exit(1)
                    elif i["XM"] in self.course[course] and i["KTRS"] >= i["KTRL"]:
                        if i["XM"] not in teachers_[course]:
                            teachers_[course].append(i["XM"])
                        else:
                            continue
                        logging.info("课堂人数仍为满, 继续等待!")
                        logging.info(datetime.now())
            time.sleep(1)

    def run(self, T: str):
        date = time.mktime(time.strptime(str(datetime.today().year) + "/" + T, "%Y/%m/%d/%H/%M"))
        if self.function == "Attack":
            while True:
                diff = time.time() - date
                if diff > 0:
                    self.init_()
                    self.muti_post()
                    break
                else:
                    logging.info(f"等待中, 剩余{int(-diff)} secs 开始")
                    if -diff > 3:
                        time.sleep(-diff - 3)
                    else:
                        time.sleep(0.001)
                    continue
        elif self.function == "Rob":
            self.init_()
            self.rob_class()
