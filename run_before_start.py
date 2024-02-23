import time
import aiohttp
import json
import asyncio


async def post_request(value: dict, XQH: str, courseNum: int):
    async with aiohttp.ClientSession() as session:
        session.cookie_jar.update_cookies(cookies)
        datas = {
            "ktbh": XQH + value["KCBH"] + "00" + str(courseNum),
            "xqh": XQH,
            "kcbh": value["KCBH"],
            "fzid": value["FZID"],
            "faid": value["ID"],
            "sfid": userId,
        }
        async with session.post(
                url="http://wsxk.hust.edu.cn/zyxxk/Stuxk/addStuxkIsxphx",
                data=datas,
        ) as response:
            try:
                assert response.status == 200
                json = await response.json()
                if json["code"] != 0:
                    print(f"{json['msg']}")
            except AssertionError:
                print(await response.text())
                return


async def main(grade_: int):
    XQH = getXQH()
    semester = ""
    if XQH[4] == "1":
        semester = "fall"
    else:
        semester = "spring"
    datafile = f"src/{grade_}_{semester}_course.json"
    with open(datafile, "r", encoding="utf8") as f:
        datas = json.load(f)
        tasks = []
        for name, course in datas.items():
            for item in courses:
                if name == item[0]:
                    tasks.append(
                        post_request(
                            {
                                "ID": course["ID"],
                                "KCBH": course["KCBH"],
                                "FZID": course["FZID"],
                            },
                            XQH, item[1]
                        )
                    )
    await asyncio.gather(*tasks)


def getXQH() -> str:
    # 获取年份XQ
    year = time.localtime().tm_year
    # 获取月份
    month = time.localtime().tm_mon
    if month < 6:
        XQH = str(year - 1) + "2"
    else:
        XQH = str(year) + "1"
    return XQH


if __name__ == "__main__":
    """
    userId: 学号
    grade: 年级, 1 为大一, 2 为大二, 3 为大三, 4 为大四, 用于获取课程信息文件
    cookies: 登录后的cookies
    courses: tuple, 课程名, 课堂号, 课堂号为 1 为课堂一, 2 为课堂二, 以此类推
    Time: 选课开始时间
    """
    userId = "Your student ID"
    grade = 3
    cookies = "Your cookies"
    cookies = dict(i.split("=") for i in cookies.split("; "))
    courses = [
        ("并行编程原理与实践", 1),
        ("数字图像处理", 1),
        ("云计算与虚拟化", 1),
        ("大数据存储系统与管理", 1),
    ]
    Time = "2024/2/27 16:00:00"  # 实际上可以不用等待选课开始, 直接选课
    # wait until the time is up
    start_time = time.mktime(time.strptime(Time, "%Y/%m/%d %H:%M:%S"))
    if time.time() < start_time:
        print(f"等待选课开始, 距离选课开始还有{start_time - time.time()}秒")
        time.sleep(start_time - time.time())
    asyncio.run(main(grade))
