class professionalCourse:
    def __init__(self, loginSession):
        self.loginSession = loginSession
        self.course_credit = {}
        self.init()

    def init(self):
        self.loginSession.get("http://hubs.hust.edu.cn/hustpass.action")
        res = self.loginSession.post(
            "http://hubs.hust.edu.cn/plan/Plan_queryPlanModuleCourse.action",
            data={"nj": "2021", "zybh": "004068", "mkid": "2708"},
        )
        for i in res.json()["data"]:
            self.course_credit[i["KCMC"]] = []
            self.course_credit[i["KCMC"]].append(i["KCZXF"])
            temp = self.loginSession.post(
                "http://hubs.hust.edu.cn/plan/Plan_queryXdbj.action",
                data={"kcbh": i["KCBH"]},
            )
            self.course_credit[i["KCMC"]].append(temp.json()["result"])

    def sum(self) -> int:
        sum_credit = 0
        for i in self.course_credit.values():
            if i[1]:
                sum_credit += i[0]
        return sum_credit

    def detail(self) -> dict:
        return self.course_credit
