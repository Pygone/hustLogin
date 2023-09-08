import pytesseract

from LoginSession import LoginSession
from operate import operator

userId = "xxx"
password = "xxx"
if __name__ == "__main__":
    try:
        pytesseract.get_tesseract_version()
        session = LoginSession(userId=userId, password=password)
        ex = operator(session, userId)
        ex.course({"节奏世界": "李娜"}, "2021-09-20 08:00:00", "Attack")
        ex.school_card(100, "xxx")
        print(ex.public_course(["节奏世界"]))
    except pytesseract.TesseractNotFoundError:
        print("your device haven't installed tesseract yet")
