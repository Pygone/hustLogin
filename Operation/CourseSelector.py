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


async def execute_script(session, text):
    """
    Executes a script by sending a POST request to the specified URL with the provided data.

    Args:
        session (aiohttp.ClientSession): The client session used to send the request.
        text (str): The text containing the data to be extracted and sent in the request.

    Raises:
        AssertionError: If the response status is not 200.

    Returns:
        None
    """
    pattern = re.compile(r'name="(.*)" value="(.*)"/?>')
    resp = pattern.findall(text)
    data = {}
    for i in resp:
        data[i[0]] = i[1]
    async with session.post("http://wsxk.hust.edu.cn/zyxxk/nlogin", data=data) as resp:
        assert resp.status == 200


async def post_request(session, course, value):
    async with session.post(
        url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/addStuxkIsxphx",
        data=value,
    ) as response:
        assert response.status == 200
        json = await response.json()
        if json["code"] == 0:
            print(f"{course} 选课成功")
        else:
            print(f"{course} 选课失败")


async def post_requests(session, datas):
    """
    Sends enrollment requests for the specified courses.

    Args:
    - session: The aiohttp ClientSession object.
    - datas: The enrollment request data.

    Returns:
    - None
    """
    tasks = [post_request(session, course, value) for course, value in datas.items()]
    await asyncio.gather(*tasks)


async def get_course(session) -> Any | None:
    """
    Retrieves the available courses from the server.

    Args:
    - session: The aiohttp ClientSession object.

    Returns:
    - dict: A dictionary containing the retrieved courses.
    """
    async with session.get(
        "http://wsxk.hust.edu.cn/xklogin.jsp?url=http://wsxk.hust.edu.cn/zyxxk/nlogin"
    ) as response:
        assert response.status == 200
        text = await response.text()  # this is a script
        await execute_script(session, text)
    data = {"page": 1, "limit": 10, "fzxkfs": "", "xkgz": 1}
    async with session.post(
        url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/getXsFaFZkc",
        data=data,
    ) as response:
        assert response.status == 200
        resp = await response.json()
        if resp["count"] == 0:
            return None
        return resp["data"]


class CourseSelector:
    """
    A class for selecting and enrolling in courses.

    Attributes:
    - userId (str): The user ID of the student.
    - courses (dict): A dictionary of courses to be selected, with course names as keys and teacher names as values.
    - cookies (str): The cookies used for authentication.

    Methods:
    - get_course(session): Retrieves the available courses from the server.
    - parse_course(courses): Parses the retrieved courses and filters them based on the specified courses.
    - get_class_ids(session, request_dict): Retrieves the class IDs for the specified courses.
    - get_class_id(session, data, course): Retrieves the class ID for a specific course.
    - post_requests(session, datas): Sends enrollment requests for the specified courses.
    - run(): Executes the course selection process.
    """

    def __init__(self, userId, courses=None, cookies=None):
        if courses is None:
            courses = {}
        self.courses = courses
        self.XQH = None
        self.userId = userId
        if cookies is None:
            print("No cookies provided")
            return
        self.cookies = cookies

    def parse_course(self, courses: dict) -> dict:
        """
        Parses the retrieved courses and filters them based on the specified courses.

        Args:
        - courses (dict): A dictionary containing the retrieved courses.

        Returns:
        - dict: A dictionary containing the filtered courses.
        """
        result = {}
        for course in courses:
            for key in self.courses.keys():
                if course["KCMC"] == key:
                    ID = course["ID"]
                    KCBH = course["KCBH"]
                    FZID = course["FZID"]
                    self.XQH = course["XQH"]
                    result[key] = {"ID": ID, "KCBH": KCBH, "FZID": FZID}
        return result

    async def get_course_data(self, session, course, value):
        data = {
            "page": 1,
            "limit": 10,
            "fzid": value["FZID"],
            "kcbh": value["KCBH"],
            "sfid": self.userId,
            "faid": value["ID"],
            "id": value["ID"],
        }
        return course, {
            "ktbh": await self.get_class_id(session, data, course),
            "xqh": self.XQH,
            "kcbh": value["KCBH"],
            "fzid": value["FZID"],
            "faid": value["ID"],
            "sfid": self.userId,
        }

    async def get_class_ids(self, session, request_dict: dict) -> dict:
        """
        Retrieves the class IDs for the specified courses.

        Args:
        - session: The aiohttp ClientSession object.
        - request_dict (dict): A dictionary containing the filtered courses.

        Returns:
        - dict: A dictionary containing the class IDs for the specified courses.
        """
        tasks = [
            self.get_course_data(session, course, value)
            for course, value in request_dict.items()
        ]
        results = await asyncio.gather(*tasks)
        return {course: data for course, data in results}

    async def get_class_id(self, session, data, course):
        """
        Retrieves the class ID for a specific course.

        Args:
        - session: The aiohttp ClientSession object.
        - data: The data payload for the request.
        - course (str): The name of the course.

        Returns:
        - str: The class ID for the specified course.
        """
        async with session.post(
            url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/getFzkt",
            data=data,
        ) as response:
            assert response.status == 200
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
                logging.info(f"距离选课开始还有{int(-diff)}秒")
                if -diff > 3:
                    time.sleep(-diff - 3)
                else:
                    time.sleep(0.01)
        asyncio.run(self.main())

    async def main(self):
        """
        The main function for the CourseSelector class.
        It performs the following steps:
        1. Creates a client session using aiohttp.
        2. Updates the session's cookies with the provided cookies.
        3. Retrieves the available courses using the get_course method.
        4. If no courses are available, prints a message and exits.
        5. Parses the retrieved courses into a dictionary using the parse_course method.
        6. Retrieves the class IDs for the courses using the get_class_ids method.
        7. Sends post requests for the selected courses using the post_requests method.
        """
        async with aiohttp.ClientSession() as session:
            session.cookie_jar.update_cookies(cookies=self.cookies)
            courses = await get_course(session)
            if courses is None:
                print("No courses available")
                print("Exiting...")
                return
            raw_request_dict = self.parse_course(courses)
            request_dict = await self.get_class_ids(session, raw_request_dict)
            await post_requests(session, request_dict)
