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
        print(ex.transcript())
    except pytesseract.TesseractNotFoundError:
        print("your device haven't installed tesseract yet")
