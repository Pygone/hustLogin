from PIL import Image, ImageOps
from pytesseract import image_to_string


# 借用libhustpass


def depoint(img):
    pic_data = img.load()
    w, h = img.size
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            count = 0
            if pic_data[x, y - 1] > 245:  # 上
                count = count + 1
            if pic_data[x, y + 1] > 245:  # 下
                count = count + 1
            if pic_data[x - 1, y] > 245:  # 左
                count = count + 1
            if pic_data[x + 1, y] > 245:  # 右
                count = count + 1
            if pic_data[x - 1, y - 1] > 245:  # 左上
                count = count + 1
            if pic_data[x - 1, y + 1] > 245:  # 左下
                count = count + 1
            if pic_data[x + 1, y - 1] > 245:  # 右上
                count = count + 1
            if pic_data[x + 1, y + 1] > 245:  # 右下
                count = count + 1
            if count > 5:
                pic_data[x, y] = 255
    return img


def deCaptcha(imageContent):
    res = [{}, {}, {}, {}]

    def analyseCode(c, i):
        code_map = {0: [1, 2, 3], 1: [0, 1, 2, 3], 2: [0, 1, 2], 3: [0, 1, 3]}
        while len(c) < 3 or (i == 1 and len(c) <= 3):
            c += "-"
        if i == 0 and len(c) > 3:
            c = c[1:]
        if i == 3 and len(c) > 3:
            c = c[:2] + c[3]
        for j in range(len(code_map[i])):
            if c[j] == "-":
                break
            if c[j] not in res[code_map[i][j]].keys():
                res[code_map[i][j]][c[j]] = 1
            else:
                res[code_map[i][j]][c[j]] += 1

    with Image.open(imageContent) as imageObject:
        i = 0
        try:
            imageObject.seek(0)
            while True:
                grayImage = ImageOps.expand(
                    imageObject.convert("L"), border=5, fill="white"
                )
                binarizedImage = grayImage.point(lambda i: i == 255 and 255)
                depointedImage = depoint(binarizedImage)
                code = image_to_string(
                    depointedImage,
                    config="--psm 11 --oem 3 -c tessedit_char_whitelist=aGQOo0123456789",
                )
                code = (
                    code.replace("o", "0")
                    .replace("Q", "0")
                    .replace("O", "0")
                    .replace("G", "6")
                    .replace("a", "0")
                )
                analyseCode(code.strip(), i)
                i += 1
                imageObject.seek(i)
        except:
            pass
    code = ""
    for i in res:
        code += str(max(i, key=i.get))
    return code
