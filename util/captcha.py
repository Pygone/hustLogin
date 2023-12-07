from PIL import Image
from pytesseract import image_to_string


def deCaptcha(imageContent):
    img_list = [img.copy().convert('L') for img in Image.open(imageContent).sequence]
    width, height = img_list[0].size
    img_merge = Image.new(mode='L', size=(width + 20, height + 20), color=255)
    for pos in [(x, y) for x in range(width) for y in range(height)]:
        if sum([img.getpixel(pos) < 254 for img in img_list]) >= 3:
            img_merge.putpixel((pos[0] + 15, pos[1] + 10), 0)
    return image_to_string(img_merge, config='-c tessedit_char_whitelist=0123456789 --psm 11').strip()
