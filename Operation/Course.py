import re

import requests
from bs4 import BeautifulSoup


class Course(requests.Session):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.Courses = {}
        self.func()

    def add(self, text: str):
        lines = text.split('\n')
        courseName = lines[0]
        teacherName = lines[2]
        idx = 10
        schedule = {"周次": [], "星期": [], "节次": [], "地点": []}
        scheduleKeys = list(schedule.keys())
        while idx < len(lines):
            for i in range(len(scheduleKeys)):
                schedule[scheduleKeys[i]].append(lines[idx + i])
            idx += 4
        Course = {
            "teacherName": teacherName,
            "schedule": schedule
        }
        self.Courses[courseName] = Course

    def func(self):
        self.get(self.url)
        res = self.get("http://hub.m.hust.edu.cn/kcb/todate/namecourse.action?kcname=&lsname=")
        soup = BeautifulSoup(res.text, features="html.parser")
        res = soup.find_all("li")
        for i in res:
            t = re.sub('\r|\t', '', i.text).strip()
            t = t.replace(' ', '')
            t = re.sub('\n+', '\n', t)
            pattern = re.compile("人数/容量：(.*)\n开课对象", re.DOTALL)
            temp = re.search(pattern, t).group(1)
            t = t.replace(temp, temp.replace('\n', ''))
            self.add(t)
