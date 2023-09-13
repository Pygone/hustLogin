import re
import time

from bs4 import BeautifulSoup


class publicCourse:
    def __init__(self, loginSession, query: list):
        self.loginSession = loginSession
        self.query = query
        self.valid_list = list()

    def get_all_courseParams(self, course_id):
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
            self.valid_list.append(res_dict.copy())

    def test_if_conflict(self):
        validList = self.valid_list.copy()
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
                    self.valid_list.remove(course_dict_)
                elif "已经选修该公共任选课，不能够再选修该公共任选课" in msg:
                    print("您已选修该课程", course_dict_["kcmc"])
                    self.valid_list.remove(course_dict_)
                elif "选课失败，课堂人数已满！" in msg:
                    continue
                else:
                    print(msg)
                    self.valid_list.remove(course_dict_)
            except:
                print("存在冲突")
                self.valid_list.remove(course_dict_)

    def run(self):
        self.loginSession.get("http://wsxk.hust.edu.cn/hustpass2.action")
        time.sleep(0.5)
        self.loginSession.get(
            "http://wsxk.hust.edu.cn/studentControl!chooseSystem.action?xkxt=zxq"
        )
        for course in self.query:
            res = self.loginSession.post(
                "http://wsxk.hust.edu.cn/zxqstudentcourse/zxqcourses.action",
                data={"markZB": "", "ggkdll": "", "GGKDLBH": "0", "kcmc": course},
            )
            course_id = re.search("onclick=\"selectKT\(this.id,'(.*)'\)", res.text).group(1)
            self.get_all_courseParams(course_id)
        self.test_if_conflict()
        while True:
            ValList = self.valid_list.copy()
            if len(self.valid_list) == 0:
                break
            for course_dict in ValList:

                res_ = self.loginSession.post(
                    "http://wsxk.hust.edu.cn/zxqstudentcourse/zxqcoursesresult.action",
                    data=course_dict,
                )
                soup = BeautifulSoup(res_.text, features="html.parser")
                msg = soup.body.div.find_all("div")[1].ul.li.string.strip()
                if "选课失败，课堂人数已满！" in msg:
                    print(course_dict["kcmc"], msg)
                    continue
                else:
                    print(course_dict["kcmc"], "选课成功")
                    for i in ValList:
                        if i["kcmc"] == course_dict["kcmc"]:
                            self.valid_list.remove(i)
