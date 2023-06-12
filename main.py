import subprocess
import sys

from LoginSession import LoginSession

userId = "xxx"
password = "xxx"
if __name__ == "__main__":
    x = subprocess.Popen("where tesseract", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, encoding='gbk').wait()
    if x != 0:
        print("Tesseract 尚未安装完善")
        sys.exit(-1)
    ex = LoginSession(userId=userId, password=password)
    print(ex.transcript("xxx"))
