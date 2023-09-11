import pytesseract

from LoginSession import LoginSession
from operate import operator

userId = "xxx"
password = "xxx"
if __name__ == "__main__":
    try:
        pytesseract.get_tesseract_version()
        session = LoginSession(userId=userId, password=password)
        operation = operator(session, userId)
    except pytesseract.TesseractNotFoundError:
        print("your device haven't installed tesseract yet")
