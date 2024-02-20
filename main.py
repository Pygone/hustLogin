import pytesseract

from LoginSession import LoginSession
from operate import Operator

userId = "Your Student ID Here"
password = "Your Password Here"
if __name__ == "__main__":
    try:
        pytesseract.get_tesseract_version()
        session = LoginSession(userId=userId, password=password)
        operation = Operator(session, userId)
        print(operation.course({"计算机网络": "李志强"}, "2024/2/24 10:00:00"))
    except pytesseract.TesseractNotFoundError:
        print("your device haven't installed tesseract yet")
