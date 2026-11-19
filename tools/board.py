"""地震仪画笔：同一段代码，两种去处。

    b = Board.simulate()            画在电脑上，立刻出图
    b = Board.connect()             画在真机的屏幕上

孩子写的画法只有一套；换一行 `Board.` 就换目标。这就是「部署」的启蒙。

命令行语法和固件保持一字不差，所以模拟器里画出来的东西，真机上就是
同一幅画（tools/compare.py 用画布哈希验证）。
"""

import json

from render import Canvas


class BoardError(Exception):
    """孩子看得懂的出错信息，不是 Python 堆栈。"""


# ---------------------------------------------------------------- 命令解释器

_KINDS = {"px", "line", "rect", "fill", "circle", "poly", "polyc", "text",
          "clear", "show", "status", "overlay"}


def execute(canvas, line, now_ms=0):
    """执行一条 gfx 命令。返回回执字典，很多命令返回 None（静默成功）。"""
    parts = line.strip().split(None, 1)
    verb = parts[0] if parts else ""
    rest = parts[1] if len(parts) > 1 else ""

    if verb == "clear":
        canvas.clear()
        return None
    if verb == "show":
        return {"ok": True, "ops": canvas.ops}
    if verb == "status":
        return {"ok": True, "overlay": True, "ops": canvas.ops,
                "texts": len(canvas.texts), "crc": canvas.hash()}
    if verb == "overlay":
        return {"ok": True}
    if verb not in _KINDS:
        raise BoardError("我不认识这个命令：%s" % (verb or "（空）"))

    nums = []
    for token in rest.split():
        try:
            nums.append(int(token))
        except ValueError:
            break
    if verb == "px":
        _need(nums, 2, "一个点需要横、竖两个数，比如：点 10 20")
        canvas.put(nums[0], nums[1])
    elif verb == "line":
        _need(nums, 4, "一条线需要四个数：起点横、起点竖、终点横、终点竖")
        canvas.line(*nums[:4])
    elif verb in ("rect", "fill"):
        _need(nums, 4, "方框需要四个数：左边、上边、宽、高")
        canvas.rect(*nums[:4], solid=(verb == "fill"))
    elif verb == "circle":
        _need(nums, 3, "圆需要三个数：圆心横、圆心竖、半径")
        canvas.circle(*nums[:3])
    elif verb in ("poly", "polyc"):
        if len(nums) < 4:
            raise BoardError("折线至少要两个点，也就是四个数")
        pts = [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
        if len(pts) > 16:
            raise BoardError("一条折线最多 16 个点，现在有 %d 个" % len(pts))
        canvas.poly(pts, close=(verb == "polyc"))
    elif verb == "text":
        _need(nums, 2, "写字需要两个数：横、竖，然后再写内容")
        words = rest.split(None, 2)
        if len(words) < 3:
            raise BoardError("想写什么？比如：字 8 32 小明")
        canvas.text(nums[0], nums[1], words[2])
    canvas.ops += 1
    return None


def _need(nums, n, message):
    if len(nums) < n:
        raise BoardError(message)


# ---------------------------------------------------------------- 后端

class _SimBackend:
    """把命令画到内存里的 2048 字节，和固件同构。"""

    name = "模拟器"

    def __init__(self):
        self.canvas = Canvas()

    def send(self, line, expect_reply=False):
        return execute(self.canvas, line)

    def close(self):
        pass


class _RawSerial:
    """只用标准库的串口。孩子不该为了插一根 USB 线去 pip install。"""

    def __init__(self, path, baud=115200):
        import os
        import termios
        import tty
        self.fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        tty.setraw(self.fd)
        attrs = termios.tcgetattr(self.fd)
        speed = getattr(termios, "B%d" % baud)
        attrs[4] = speed
        attrs[5] = speed
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)

    def read(self, count=1, timeout=0.3):
        import os
        import select
        ready, _, _ = select.select([self.fd], [], [], timeout)
        if not ready:
            return b""
        try:
            return os.read(self.fd, count)
        except BlockingIOError:
            return b""

    def write(self, data):
        import os
        os.write(self.fd, data)

    def close(self):
        import os
        os.close(self.fd)


class _DeviceBackend:
    """把命令写进串口，让真机去画。"""

    name = "地震仪"

    def __init__(self, port=None):
        self.port = port or self._guess()
        self._serial = _RawSerial(self.port, 115200)
        self._buffer = b""
        self.canvas = Canvas()   # 本地影子，只用于预览和哈希比对
        # 打开串口会让 ESP32 复位；等它开机打完 hello 再发命令，
        # 否则第一条命令会被丢掉。
        self._wait_boot()
        self._require_drawing_firmware()

    def _require_drawing_firmware(self):
        """先确认这台设备会不会画，而不是让孩子对着没反应的屏幕等。"""
        self._serial.write(b"gfx status\n")
        try:
            self._read_reply()
        except BoardError:
            raise BoardError(
                "这台地震仪跑的是 GitHub 发布版固件，还没有画图命令。\n"
                "  要上课，需要先烧入带 gfx 的固件（v2.1.0-gfx）；\n"
                "  只想看波形，可以用 Board.simulate() 在电脑上画。"
            )

    def _wait_boot(self, seconds=6.0):
        import time
        end = time.time() + seconds
        while time.time() < end:
            chunk = self._serial.read(1, 0.3)
            if not chunk:
                continue
            self._buffer += chunk
            if not self._buffer.endswith(b"\n"):
                continue
            line, self._buffer = self._buffer.decode("utf-8", "replace").strip(), b""
            if '"type":"hello"' in line:
                return True
        return False

    @staticmethod
    def _guess():
        import glob
        ports = sorted(glob.glob("/dev/cu.usbmodem*"))
        if not ports:
            raise BoardError("没找到地震仪。检查 USB 线，或者先改成 Board.simulate()")
        return ports[0]

    def send(self, line, expect_reply=False):
        # 固件认的行首关键字是 gfx；SDK 里省掉它，孩子看到的命令短一点。
        self._serial.write(("gfx " + line + "\n").encode("utf-8"))
        # 本地影子也画一遍，这样电脑上能预览、也能比对哈希。
        execute(self.canvas, line)
        if not expect_reply:
            return None
        return self._read_reply()

    def _read_reply(self):
        import time
        end = time.time() + 2.0
        while time.time() < end:
            chunk = self._serial.read(1, 0.3)
            if not chunk:
                continue
            self._buffer += chunk
            if not self._buffer.endswith(b"\n"):
                continue
            line, self._buffer = self._buffer.decode("utf-8", "replace").strip(), b""
            if not line.startswith("{"):
                continue
            try:
                message = json.loads(line)
            except ValueError:
                continue
            # 开机 hello、状态记录等消息会插在中间，跳过它们再等回执。
            if message.get("type") != "gfx":
                continue
            return message
        raise BoardError("地震仪没有回话（可能正在预热，或者被别的程序占着）")

    def close(self):
        self._serial.close()


# ---------------------------------------------------------------- 画笔

class Board:
    """地震仪屏幕。256×64 个格子，每个格子只有亮和灭。"""

    def __init__(self, backend):
        self._backend = backend

    # ---- 两种去处 ----
    @classmethod
    def simulate(cls):
        return cls(_SimBackend())

    @classmethod
    def connect(cls, port=None):
        return cls(_DeviceBackend(port))

    @property
    def where(self):
        return self._backend.name

    @property
    def canvas(self):
        return self._backend.canvas

    def close(self):
        self._backend.close()

    # ---- 画 ----
    def clear(self):
        self._send("clear")

    def px(self, x, y):
        self._send("px %d %d" % (x, y))

    def line(self, x1, y1, x2, y2):
        self._send("line %d %d %d %d" % (x1, y1, x2, y2))

    def rect(self, x, y, w, h):
        self._send("rect %d %d %d %d" % (x, y, w, h))

    def fill(self, x, y, w, h):
        self._send("fill %d %d %d %d" % (x, y, w, h))

    def circle(self, cx, cy, r):
        self._send("circle %d %d %d" % (cx, cy, r))

    def poly(self, points):
        self._send("poly " + " ".join("%d %d" % (x, y) for x, y in points))

    def polyc(self, points):
        self._send("polyc " + " ".join("%d %d" % (x, y) for x, y in points))

    def text(self, x, y, s):
        self._send("text %d %d %s" % (x, y, s))

    def overlay(self, on=True):
        self._send("overlay %s" % ("on" if on else "off"))

    def show(self):
        return self._send("show", expect_reply=True)

    def status(self):
        return self._send("status", expect_reply=True)

    # ---- 看 ----
    def hash(self):
        return self.canvas.hash()

    def png(self, path, scale=4):
        self.canvas.to_png(path, scale=scale)

    def as_text(self):
        return self.canvas.to_text()

    def _send(self, line, expect_reply=False):
        result = self._backend.send(line, expect_reply=expect_reply)
        if result and result.get("ok") is False:
            raise BoardError("地震仪说：%s" % result.get("error", "画不了"))
        return result


# ---------------------------------------------------------------- 形状

def star(cx=128, cy=32, r=21):
    """五角星的五个顶点。

    五个顶点相隔 72°，但**连接顺序要隔一个连**（0→2→4→1→3），
    否则画出来是个五边形。这一步就是「数学变成图形」。
    """
    import math
    order = [0, 2, 4, 1, 3]
    return [(int(cx + r * math.cos(math.radians(-90 + 72 * i)) + 0.5),
             int(cy + r * math.sin(math.radians(-90 + 72 * i)) + 0.5)) for i in order]
