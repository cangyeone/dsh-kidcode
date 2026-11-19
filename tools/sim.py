"""把一串 gfx 命令渲染成图片，不碰设备。

    python3 tools/sim.py --out /tmp/a.png "gfx clear" "gfx circle 128 32 20" "gfx show"

也可以从文件读命令（一行一条）：
    python3 tools/sim.py --out /tmp/a.png --script demo/commands.txt

没写 gfx 前缀也没关系，两种写法都认。
"""

import argparse
import sys

import board
import render


def main():
    parser = argparse.ArgumentParser(description="离屏渲染 256×64")
    parser.add_argument("commands", nargs="*", help="gfx 命令行")
    parser.add_argument("--script", help="从文件读命令，一行一条")
    parser.add_argument("--out", default="sim.png", help="输出 PNG")
    parser.add_argument("--scale", type=int, default=4, help="放大倍数")
    parser.add_argument("--text", action="store_true", help="同时在终端打印字符画")
    args = parser.parse_args()

    lines = list(args.commands)
    if args.script:
        with open(args.script, encoding="utf-8") as f:
            lines += [line.strip() for line in f if line.strip() and not line.startswith("#")]
    if not lines:
        lines = ["gfx clear", "gfx circle 128 32 20", "gfx show"]

    canvas = render.Canvas()
    for line in lines:
        body = line[4:] if line.startswith("gfx ") else line
        board.execute(canvas, body)

    canvas.to_png(args.out, scale=args.scale)
    print("画布哈希：", canvas.hash())
    print("亮了 %d 个格子" % sum(bin(b).count("1") for b in canvas.data))
    print("图：", args.out)
    if args.text:
        print(canvas.to_text())
    if canvas.texts:
        print("注意：%d 条文字由设备字体绘制，预览图里不显示。" % len(canvas.texts))


if __name__ == "__main__":
    sys.exit(main())
