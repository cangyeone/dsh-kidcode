"""256×64 单色画布：与固件 gfx.cpp 逐位一致的绘图。

这个文件只依赖 Python 标准库。它做的事情和地震仪屏幕上那 2048 字节
完全一样：每个像素一位，1 表示亮。

之所以要一模一样，是因为「先模拟后真机」只有在两边画出同一个画面时才
成立。tools/compare.py 会用画布哈希来验证这一点。
"""

WIDTH = 256
HEIGHT = 64
STRIDE = WIDTH // 8          # 每行 32 字节
BYTES = STRIDE * HEIGHT      # 一帧 2048 字节


def fnv1a(data: bytes) -> int:
    """和固件 gfx::canvasHash() 相同的哈希。"""
    h = 2166136261
    for b in data:
        h ^= b
        h = (h * 16777619) & 0xFFFFFFFF
    return h


class Canvas:
    def __init__(self):
        self.data = bytearray(BYTES)
        self.texts = []      # (x, y, 文字)，文字不进画布，和固件一致
        self.ops = 0         # 自上次 clear 之后画了几笔

    # ---- 基本操作 ----
    def clear(self):
        self.data = bytearray(BYTES)
        self.texts = []
        self.ops = 0

    def put(self, x, y):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self.data[y * STRIDE + (x >> 3)] |= 0x80 >> (x & 7)

    def get(self, x, y):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            return (self.data[y * STRIDE + (x >> 3)] >> (7 - (x & 7))) & 1
        return 0

    def hash(self):
        return fnv1a(bytes(self.data))

    # ---- 图元 ----
    def line(self, x0, y0, x1, y1):
        clipped = _clip(x0, y0, x1, y1)
        if clipped is None:
            return
        x0, y0, x1, y1 = clipped
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.put(x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def rect(self, x, y, w, h, solid=False):
        if w < 0:
            x, w = x + w, -w
        if h < 0:
            y, h = y + h, -h
        if w == 0 or h == 0:
            return
        x2, y2 = x + w - 1, y + h - 1
        if solid:
            for yy in range(y, y2 + 1):
                for xx in range(x, x2 + 1):
                    self.put(xx, yy)
            return
        self.line(x, y, x2, y)
        self.line(x2, y, x2, y2)
        self.line(x2, y2, x, y2)
        self.line(x, y2, x, y)

    def circle(self, cx, cy, r):
        r = abs(r)
        if r == 0:
            self.put(cx, cy)
            return
        x, y, err = r, 0, 1 - r
        while x >= y:
            for px, py in ((cx + x, cy + y), (cx + y, cy + x), (cx - y, cy + x),
                           (cx - x, cy + y), (cx - x, cy - y), (cx - y, cy - x),
                           (cx + y, cy - x), (cx + x, cy - y)):
                self.put(px, py)
            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x) + 1

    def poly(self, points, close=False):
        pts = list(points)
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])
        if close and len(pts) >= 2:
            self.line(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1])

    def text(self, x, y, s):
        if len(self.texts) < 8:
            self.texts.append((x, y, s[:31]))

    # ---- 导出 ----
    def to_png(self, path, scale=4, ink=(17, 24, 39), paper=(255, 255, 255)):
        parts = []
        for y in range(HEIGHT):
            row = bytearray()
            for x in range(WIDTH):
                row.extend(bytes(ink if self.get(x, y) else paper) * scale)
            scanline = b"\x00" + bytes(row)   # 每行自己的过滤字节
            parts.append(scanline * scale)
        _write_png(path, WIDTH * scale, HEIGHT * scale, b"".join(parts))

    def to_text(self, on="█", off="·"):
        return "\n".join(
            "".join(on if self.get(x, y) else off for x in range(WIDTH))
            for y in range(HEIGHT)
        )


def _clip(x0, y0, x1, y1):
    """Liang–Barsky 裁剪，和固件同名函数一致。"""
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0

    def edge(p, q):
        nonlocal t0, t1
        if p == 0:
            return q >= 0
        r = q / p
        if p < 0:
            if r > t1:
                return False
            if r > t0:
                t0 = r
        else:
            if r < t0:
                return False
            if r < t1:
                t1 = r
        return True

    if not (edge(-dx, x0) and edge(dx, WIDTH - 1 - x0)
            and edge(-dy, y0) and edge(dy, HEIGHT - 1 - y0)):
        return None
    return (int(x0 + t0 * dx + 0.5), int(y0 + t0 * dy + 0.5),
            int(x0 + t1 * dx + 0.5), int(y0 + t1 * dy + 0.5))


def write_png(path, w, h, raw):
    zlib = __import__("zlib")
    import struct

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)  # 8-bit RGB
    body = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
    body += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(body)


_write_png = write_png
