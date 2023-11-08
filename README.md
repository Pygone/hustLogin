# Hust

平平无奇的小仓库

## deps

### python-deps

```shell
pip install -r requirements.txt
```

### OCR-deps

[tesseract](https://github.com/tesseract-ocr/tesseract)  
find a suitable platform to install the ocr deps, and remember to put it into PATH, or this tool
can't find the accurate position of tesseract

## Usage

### hustLogin

in this session, user can login to the hust platform, and get the net-session of the user.
in which, user can use it to impersonate a user doing something in the hust platform.

```python
from LoginSession import LoginSession

userId = "xxx"
password = "xxx"
session = LoginSession(userId=userId, password=password)
```

below, we will list some usage of this tool.

```python
from operate import operator

operation = operator(session, userId)
```

### course_schedule

in this session, user can easily get the course schedule of the user, and the course schedule will be returned to json
format. building a schedule app of husters-only can be easier.

```python
course_info = operation.schedule()  # course_info is a json object contains the course schedule of the user.
```

### course_score

in this session, user can easily get the course score of the user, and the course score will be returned to json format.

```python
course_score = operation.transcript()  # course_score is a json object contains the course score of the user.
```

### professional course_select

in this session, user can post the request to select the course by script which is faster a lot than humans action.
func param only support "Attack" because the hust platform recently split the withdraw operation and select operation.

```python
operation.course({"图神经网络": "万瑶"}, "09/28/13/00", "Attack")
```

### badminton court select

in this session, user can post the request to select the badminton court by script which is faster a lot than humans
action.
partner is optional, if you want to specify your friend, you can add the partner info in the list
in ["password", "name", "schoolId"] format
or the script will choose your first partner you have set before.

```python
operation.badminton("2021-09-20", "08", 1, partner=["password", "name", "schoolId"])
operation.badminton("2021-09-20", "08", 1)
# both can work well
```

### school card

in this session, user can check and top up the school card by script daily in case of lack of money in school card.

```python
operation.school_card(100, "xxx")
# 100 is the amount of money you want to top up, "xxx" is the password of your school card
```

### professional course credit

in this session, user can get the professional course credit of the user.

```python
course_credit = operation.professional_credit()
```

### public course select

in this session, user can post the request to select the public course by script which is faster a lot than humans
action.

```python
operation.public_course(["节奏世界"])
```
