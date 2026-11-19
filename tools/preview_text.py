"""把画布上的文字用电脑字体画到预览图上，只为「看见大概位置」。

设备上的字是固件用自己的字体画的，像素和这里不完全一样。所以这张图是
示意图：位置准，字形只是接近。真机上的样子以真机为准。

    from preview_text import overlay
    overlay("in.png", "out.png", [(88, 26, "震"), (128, 26, "震")], scale=4)
"""


def overlay(src, dst, texts, scale=4):
    from PIL import Image, ImageDraw, ImageFont

    font_path = "/System/Library/Fonts/STHeiti Medium.ttc"
    img = Image.open(src).convert("RGB")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 12 * scale)
    for x, y, s in texts:
        draw.text((x * scale, y * scale), s, font=font, fill=(17, 24, 39))
    img.save(dst)
    return dst
