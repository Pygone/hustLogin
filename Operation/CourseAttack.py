import asyncio
import logging
import re
import sys
import time
from datetime import datetime

import aiohttp
import fake_useragent
import requests
from requests import JSONDecodeError
from requests.structures import CaseInsensitiveDict

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(
    fmt="%(message)s"
    , datefmt="%Y-%m-%d %H:%M:%S"
))
console_handler.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, handlers=[console_handler], )
user_agent = fake_useragent.UserAgent().chrome


class CourseAttack(requests.Session):
    def __init__(self, url: str, userId, course: dict, function: str = "Attack"):
        super().__init__()
        self.url = url
        self.headers = CaseInsensitiveDict({"User-Agent": user_agent})
        self.init()
        self.function = function
        self.userId = userId
        self.course = course
        self.requestList = {}
        self.XQH = None
        self.KTBH = []
        self.GetCourse()
        self.mutiGetClassId()

    async def Postmethod(self, url, data, course, teacherNum):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=data, headers=self.headers) as response:
                assert response.status == 200
                json = await response.json()
                if json["code"] == "0":
                    logging.info(f"学号为{self.userId}的同学, 您已抢到{course}:{self.course[course][teacherNum]}")
                else:
                    logging.info(json["msg"])

    async def getclassId(self, url, data, course):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=data, headers=self.headers) as response:
                assert response.status == 200
                json = await response.json()
                courseList = []
                for i in json["data"]:
                    if i["XM"] in self.course[course]:
                        courseList.append(i["KTBH"])
                self.requestList[course].append(courseList)

    def GetCourse(self):
        data = {"page": 1, "limit": 10, "fzxkfs": "", "xkgz": 1}
        res = self.post(url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/getXsFaFZkc", data=data,
                        allow_redirects=False)
        try:
            res_json = res.json()
        except JSONDecodeError:
            logging.error("Cookie 无效!")
            sys.exit(-1)
        for i in res_json["data"]:
            for j in self.course.keys():
                if i["KCMC"] == j:
                    ID = i["ID"]
                    KCBH = i["KCBH"]
                    FZID = i["FZID"]
                    self.XQH = i["XQH"]
                    self.requestList[j] = list([ID, KCBH, FZID])

    def mutiGetClassId(self):
        tasks = []
        loop = asyncio.new_event_loop()
        for course in self.course.keys():
            data = {"page": 1, "limit": 10, "fzid": self.requestList[course][2], "kcbh": self.requestList[course][1],
                    "sfid": self.userId, "faid": self.requestList[course][0], "id": self.requestList[course][0]}
            tasks.append(
                loop.create_task(
                    self.getclassId(url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/getFzkt", data=data, course=course)))
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    def mutiPost(self):
        tasks = []
        loop = asyncio.new_event_loop()
        for course in self.course.keys():
            for i in range(len(self.requestList[course][3])):
                data = {
                    "ktbh": self.requestList[course][3][i],
                    "xqh": self.XQH,
                    "kcbh": self.requestList[course][1],
                    "fzid": self.requestList[course][2],
                    "faid": self.requestList[course][0],
                    "sfid": self.userId
                }
                tasks.append(
                    loop.create_task(
                        self.Postmethod(url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/addStuxkIsxphx", data=data,
                                        course=course, teacherNum=i)))
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    def RobClass(self):
        while True:
            for course in self.course.keys():
                data = {"page": 1, "limit": 10, "fzid": self.requestList[course][2],
                        "kcbh": self.requestList[course][1],
                        "sfid": self.userId, "faid": self.requestList[course][0], "id": self.requestList[course][0]}
                res = self.post(url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/getFzkt", data=data)
                resjson = res.json()
                for i in resjson["data"]:
                    if i["XM"] in self.course[course] and i["KTRS"] < i["KTRL"]:
                        response = self.post(url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/addStuxkIsxphx", data={
                            "ktbh": i["KTBH"],
                            "xqh": self.XQH,
                            "kcbh": self.requestList[course][1],
                            "fzid": self.requestList[course][2],
                            "faid": self.requestList[course][0],
                            "sfid": self.userId
                        })
                        json = response.json()
                        if json["code"] == "0":
                            logging.info(f"学号为{self.userId}的同学, 您已抢到{course}:{i['XM']}")
                            sys.exit(-1)
                        elif json['msg'] == '当前学期或之前学期已选该课程，不可重复选择，可在‘选课记录’中查看！':
                            logging.info(json['msg'])
                            sys.exit(-1)
                        else:
                            logging.info(json["msg"])
                            time.sleep(10)
                    elif i["XM"] in self.course[course] and i["KTRS"] >= i["KTRL"]:
                        logging.info("课堂人数仍为满, 继续等待!")
                        time.sleep(10)

    def run(self, T: str):
        if self.function == "Attack":
            while True:
                date = datetime.strptime(str(datetime.today().year) + "/" + T, '%Y/%m/%d/%H/%M')
                diff = (datetime.now() - date)
                diff = diff.days * 86400 + diff.seconds
                if diff > 0:
                    self.mutiPost()
                    break
                else:
                    logging.info(f"等待中, 剩余{-diff}secs 开始自动抢课")
                    if -diff > 10:
                        time.sleep(-diff - 10)
                    else:
                        time.sleep(1)
                    continue
        elif self.function == "Rob":
            self.RobClass()

    @staticmethod
    def analyseHtml(html):
        res = html.replace("/>", ">")
        res = re.findall('name=(.*) value=(.*)>', res)
        params = {}
        for i in res:
            params[i[0].strip('"')] = i[1].strip('"')
        return params

    def init(self):
        self.get(self.url)
        res = self.get("http://wsxk.hust.edu.cn/xklogin.jsp?url=http://wsxk.hust.edu.cn/zyxxk/nlogin").text
        params = self.analyseHtml(res)
        self.post("http://wsxk.hust.edu.cn/zyxxk/nlogin", data=params)
