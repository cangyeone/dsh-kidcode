"""第 3 课：函数 = 印章。

刻一枚印章，只写一次；想盖几次盖几次。
    python3 zhen.py             电脑上看
    python3 zhen.py --device    送到真机
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))

import board   # noqa: E402


def yinzhang(pen, x):
    """一枚印章：盖一次「震」字。位置由 x 决定。"""
    pen.text(x, 26, "震")


def main():
    device = "--device" in sys.argv
    pen = board.Board.connect() if device else board.Board.simulate()
    print("画在：", "地震仪" if device else "电脑（加 --device 就送到真机）")

    places = (88, 128, 168)       # 改这里的一个数，字就会挪
    pen.clear()
    for x in places:              # 印章不变，只换位置
        yinzhang(pen, x)
    pen.show()
    print("三个字的位置：", places)

    pen.png(os.path.join(HERE, "canvas.png"), scale=4)
    try:                          # 电脑字体画一张示意图，位置准
        from preview_text import overlay
        overlay(os.path.join(HERE, "canvas.png"),
                os.path.join(HERE, "zhen.png"), pen.canvas.texts, scale=4)
        print("示意图：zhen.png")
    except ImportError:
        print("没装 Pillow，只看 canvas.png 里的空画布")
    pen.close()


if __name__ == "__main__":
    main()
