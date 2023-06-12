import time

from PIL import Image, ImageOps
from pytesseract import image_to_string


# 挪用libhustpass

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
    with Image.open(imageContent) as imageObject:
        imageObject.seek(1)
        grayImage = ImageOps.expand(imageObject.convert("L"), border=5, fill='white')
    binarizedImage = grayImage.point(lambda i: i == 255 and 255)
    depointedImage = depoint(binarizedImage)
    code = image_to_string(depointedImage, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789')
    return code.strip()
