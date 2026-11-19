"""地震科普 第 1 课：敲一下桌子，看看振动长什么样。

    python3 knock.py

程序会等你敲一下桌子，然后录 3 秒，把波形画在终端里。
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))

import seismo   # noqa: E402


def main():
    quake = seismo.Seismo.connect()
    print("连上地震仪了。")

    input("现在用手指敲一下桌子，然后按回车：")

    quake.start()
    data = list(quake.samples(3.0))
    quake.close()

    print()
    print(seismo.waveform_text(data))
    print()
    print("最大的那一下：", round(seismo.peak(data)), "µV")
    print("来回摆动了", seismo.zero_crossings(data), "次")


if __name__ == "__main__":
    main()
