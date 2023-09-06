from PIL import Image
from pytesseract import image_to_string


# 借用libhustpass


def deCaptcha(imageContent):
    img_list = []
    with Image.open(imageContent) as img_gif:
        for i in range(img_gif.n_frames):
            img_gif.seek(i)
            img_list.append(img_gif.copy().convert('L'))
    width, height = img_list[0].size
    img_merge = Image.new(mode='L', size=(width + 10, height + 10), color=255)
    for pos in [(x, y) for x in range(width) for y in range(height)]:
        if sum([img.getpixel(pos) < 254 for img in img_list]) >= 3:
            img_merge.putpixel((pos[0] + 5, pos[1] + 5), 0)
    code = image_to_string(img_merge, config='-c tessedit_char_whitelist=0123456789 --psm 11')
    return code.strip()
