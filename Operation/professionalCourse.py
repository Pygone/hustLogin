import asyncio


class ProfessionalCourse:
    def __init__(self, login_session):
        self.login_session = login_session
        self.course_credit = {}
        asyncio.run(self.populate_course_credit())

    async def __get_credit(self, course: dict):
        datas = self.login_session.post(
            "http://hubs.hust.edu.cn/plan/Plan_queryXdbj.action",
            data={"kcbh": course["KCBH"]},
        ).json()
        if datas["result"]:
            self.course_credit[course["KCMC"]] = course["KCZXF"]

    async def populate_course_credit(self):
        self.login_session.get("http://hubs.hust.edu.cn/hustpass.action")
        response = self.login_session.post(
            "http://hubs.hust.edu.cn/plan/Plan_queryPlanModuleCourse.action",
            data={"nj": "2021", "zybh": "004068", "mkid": "2708"},  # TODO 不同年级 不同专业 mkid不同
        ).json()
        tasks = []
        for course in response["data"]:
            tasks.append(self.__get_credit(course))
        await asyncio.gather(*tasks)

    def total_credit(self) -> int:
        return sum(credit for credit in self.course_credit.values())

    def course_details(self) -> dict:
        # 返回格式化的字典
        self.course_credit["总学分"] = self.total_credit()
        return self.course_credit
