class ProfessionalCourse:
    def __init__(self, login_session):
        self.login_session = login_session
        self.course_credit = {}
        self.populate_course_credit()

    def populate_course_credit(self):
        self.login_session.get("http://hubs.hust.edu.cn/hustpass.action")
        response = self.login_session.post(
            "http://hubs.hust.edu.cn/plan/Plan_queryPlanModuleCourse.action",
            data={"nj": "2021", "zybh": "004068", "mkid": "2708"},
        )
        for course in response.json()["data"]:
            self.course_credit[course["KCMC"]] = [course["KCZXF"]]
            temp = self.login_session.post(
                "http://hubs.hust.edu.cn/plan/Plan_queryXdbj.action",
                data={"kcbh": course["KCBH"]},
            )
            self.course_credit[course["KCMC"]].append(temp.json()["result"])

    def total_credit(self) -> int:
        return sum(credit[0] for credit in self.course_credit.values() if credit[1])

    def course_details(self) -> dict:
        return self.course_credit
