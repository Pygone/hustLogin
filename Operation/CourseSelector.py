import time
from typing import Any

import aiohttp
import asyncio
import logging
import sys
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)


async def execute_script(session: aiohttp.ClientSession, text: str):
    pattern = re.compile(r'name="(.*)" value="(.*)"/?>')
    resp = pattern.findall(text)
    data = {}
    for i in resp:
        data[i[0]] = i[1]
    async with session.post("http://wsxk.hust.edu.cn/zyxxk/nlogin", data=data) as resp:
        try:
            assert resp.status == 200
        except AssertionError:
            print(await resp.text())
            return


async def update_session(session: aiohttp.ClientSession):
    async with session.get(
        "http://wsxk.hust.edu.cn/xklogin.jsp?url=http://wsxk.hust.edu.cn/zyxxk/nlogin"
    ) as response:
        try:
            assert response.status == 200
        except AssertionError:
            print(await response.text())
            return
        await execute_script(session, await response.text())


async def get_courses(session: aiohttp.ClientSession) -> list[Any] | None | Any:
    data = {"page": 1, "limit": 10, "fzxkfs": "", "xkgz": 1}
    async with session.post(
        url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/getXsFaFZkc",
        data=data,
        allow_redirects=False,
    ) as response:
        if response.status != 200:
            await update_session(session)
            return await get_courses(session)
        try:
            assert response.status == 200
        except AssertionError:
            print(await response.text())
            return None
        resp = await response.json()
        if resp["count"] == 0:
            time.sleep(0.5)
            return await get_courses(session)
        return resp["data"]


class CourseSelector:
    def __init__(self, userId: str, courses=None, cookies=None):
        if courses is None:
            courses = {}
        self.courses: dict[str, str] = courses
        self.XQH: str = ""
        self.userId: str = userId
        if cookies is None:
            print("No cookies provided")
            return
        self.cookies = cookies

    async def post_requests(self, courses: list[dict], session: aiohttp.ClientSession):
        tasks = []
        for course in courses:
            for key in self.courses.keys():
                if course["KCMC"] == key:
                    self.XQH = course["XQH"]
                    tasks.append(
                        self.post_request(
                            session,
                            {
                                "ID": course["ID"],
                                "KCBH": course["KCBH"],
                                "FZID": course["FZID"],
                            },
                            key,
                        )
                    )
        await asyncio.gather(*tasks)

    async def post_request(
        self, session: aiohttp.ClientSession, value: dict, course: str
    ):
        data = {
            "page": 1,
            "limit": 10,
            "fzid": value["FZID"],
            "kcbh": value["KCBH"],
            "sfid": self.userId,
            "faid": value["ID"],
            "id": value["ID"],
        }
        ktbh = await self.get_class_id(session, data, course)
        if ktbh is None:
            return
        datas = {
            "ktbh": ktbh,
            "xqh": self.XQH,
            "kcbh": value["KCBH"],
            "fzid": value["FZID"],
            "faid": value["ID"],
            "sfid": self.userId,
        }
        async with session.post(
            url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/addStuxkIsxphx",
            data=datas,
        ) as response:
            try:
                assert response.status == 200
                json = await response.json()
                if json["code"] == 0:
                    print(f"{course} 选课成功")
                else:
                    print(f"{course} {json['msg']}")
            except AssertionError:
                print(await response.text())
                return

    async def get_class_id(
        self, session: aiohttp.ClientSession, data: dict, course: str
    ) -> Any | None:
        async with session.post(
            url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/getFzkt",
            data=data,
        ) as response:
            try:
                assert response.status == 200
            except AssertionError:
                print("{} 课堂信息获取失败".format(course))
                return None
            json = await response.json()
            for i in json["data"]:
                if i["XM"] == self.courses[course]:
                    return i["KTBH"]

    def run(self, Time: str = ""):
        """
        Executes the course selection process.

        Returns:
        - None
        """
        start_time = time.mktime(time.strptime(Time, "%Y/%m/%d %H:%M:%S"))
        while True:
            diff = time.time() - start_time
            if diff > 0:
                break
            else:
                if -diff > 3:
                    logging.info(f"距离选课开始还有{-diff}秒")
                    time.sleep(-diff - 3)
                else:
                    time.sleep(0.01)
        asyncio.run(self.main())

    async def main(self):
        async with aiohttp.ClientSession() as session:
            session.cookie_jar.update_cookies(cookies=self.cookies)
            courses = await get_courses(session)
            if courses is None:
                print("No courses available")
                print("Exiting...")
                return
            await self.post_requests(courses, session)
