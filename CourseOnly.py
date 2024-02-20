cookies = "Your cookies"
cookies = dict(i.split("=") for i in cookies.split("; "))

user_id = "Your student ID"
courses = {"计算机网络": "李志强"}
time_ = "2024/2/24 10:00:00"

if __name__ == "__main__":
    from Operation.CourseSelector import CourseSelector

    course = CourseSelector(user_id, courses, cookies)
    course.run(time_)
