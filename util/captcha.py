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


def deCaptcha(imageContent, maxConfirmDepoint=10):
    with Image.open(imageContent) as imageObject:
        imageObject.seek(1)
        grayImage = ImageOps.expand(imageObject.convert("L"), border=5, fill='white')
    binarizedImage = grayImage.point(lambda i: i == 255 and 255)
    depointedImage = depoint(binarizedImage)
    ret = "0000"
    while maxConfirmDepoint > 0:
        depointedImage = depoint(depointedImage)
        code1 = image_to_string(depointedImage, config='--psm 10 --oem 3 -c tessedit_char_whitelist=Oo0123456789')
        depointedImage = depoint(depointedImage)
        code2 = image_to_string(depointedImage, config='--psm 10 --oem 3 -c tessedit_char_whitelist=Oo0123456789')
        depointedImage = depoint(depointedImage)
        code3 = image_to_string(depointedImage, config='--psm 10 --oem 3 -c tessedit_char_whitelist=Oo0123456789')
        if code1 == code2 or code1 == code3:
            ret = code1
            break
        if code2 == code3:
            ret = code2
            break
        maxConfirmDepoint -= 1
    return "".join([x.replace("o", "0").replace("O", "0") for x in ret if x in "Oo0123456789"])
