"""验证「模拟器」和「真机」画出的是同一幅画。

两边跑同一串命令，然后比较画布哈希（固件 gfx::canvasHash 与 render.fnv1a
是同一个算法）。哈希相同 = 逐位相同。

    python3 tools/compare.py            # 自动找串口
    python3 tools/compare.py /dev/cu.usbmodem14401
"""

import sys

import board


def drawings():
    """每一组都返回 (名字, 画笔动作)。"""
    yield "一个点", lambda b: b.px(10, 20)
    yield "一条线", lambda b: b.line(0, 32, 255, 32)
    yield "斜线", lambda b: b.line(3, 3, 200, 60)
    yield "方框", lambda b: b.rect(20, 10, 100, 40)
    yield "实心块", lambda b: b.fill(10, 10, 30, 20)
    yield "圆", lambda b: b.circle(128, 32, 25)
    yield "五角星", lambda b: b.polyc(board.star())
    yield "折线", lambda b: b.poly([(0, 0), (100, 60), (200, 10), (255, 63)])
    yield "越界裁剪", lambda b: b.line(-100, -100, 300, 200)
    yield "组合", lambda b: (b.circle(64, 32, 20), b.line(0, 0, 255, 63),
                             b.rect(200, 40, 40, 20))


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else None

    sim = board.Board.simulate()
    expected = {}
    for name, draw in drawings():
        sim.clear()
        draw(sim)
        expected[name] = sim.hash()

    try:
        device = board.Board.connect(port)   # 连接时会等设备开机
    except board.BoardError as error:
        print("连不上能画图的设备：%s" % error)
        print("模拟器本身没问题，这一项等固件恢复后再验。")
        return 2
    print("设备：已连接（%s）" % device.where)

    failures = 0
    for name, draw in drawings():
        device.clear()
        draw(device)
        device.show()
        got = device.status()["crc"]
        ok = got == expected[name]
        failures += 0 if ok else 1
        print("%-8s %s  模拟器=%10d 真机=%10d" % (name, "一致" if ok else "不同", expected[name], got))

    device.close()
    if failures:
        print("\n%d 组不一致：模拟器和固件画法已经分叉，先修这个再给小孩用。" % failures)
        return 1
    print("\n全部一致：模拟器画出来的，就是地震仪屏幕上亮起来的。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
