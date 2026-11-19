"""第 4 课：画一个五角星。

先在你的电脑上画出来，看满意了再送到地震仪上。
    python3 star.py             电脑上看
    python3 star.py --device    送到真机
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))

import board   # noqa: E402


def main():
    if "--device" in sys.argv:
        pen = board.Board.connect()
        print("画在：地震仪")
    else:
        pen = board.Board.simulate()
        print("画在：电脑（加 --device 就送到真机）")

    star = board.star(cx=128, cy=32, r=21)

    pen.clear()
    pen.polyc(star)
    pen.show()

    print("五个顶点：", " ".join("%d,%d" % p for p in star))
    print("亮了多少个格子：", sum(bin(b).count("1") for b in pen.canvas.data))

    pen.png(os.path.join(HERE, "star.png"), scale=4)
    print("图存到：", os.path.join(HERE, "star.png"))
    pen.close()


if __name__ == "__main__":
    main()
