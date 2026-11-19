"""地震仪的数据接口：把设备当成一台真的地震台。

编程线用 board.py 画屏幕；地震线用这个文件读数据。
两者都只用标准库，孩子那边零安装。

    from seismo import Seismo
    s = Seismo.connect()
    s.start()                      # 打开数据流（约 31 秒模型预热期间也能读）
    for t, uv in s.samples(5):     # 读 5 秒
        ...
    s.stop()
"""

import json
import time

from board import BoardError, _RawSerial


class Seismo:
    def __init__(self, port=None, serial=None):
        self._buffer = b""
        self.streaming = False
        if serial is not None:
            self._serial = serial
        else:
            self._serial = _RawSerial(port or self._guess(), 115200)
            self._wait_boot()

    @classmethod
    def connect(cls, port=None):
        return cls(port=port)

    @staticmethod
    def _guess():
        import glob
        ports = sorted(glob.glob("/dev/cu.usbmodem*"))
        if not ports:
            raise BoardError("没找到地震仪。检查 USB 线。")
        return ports[0]

    def _wait_boot(self, seconds=6.0):
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

    # ---- 命令 ----
    def _send(self, line):
        self._serial.write((line + "\n").encode("utf-8"))

    def start(self):
        """开始接收原始采样。设备会先回一条 hello。"""
        self._buffer = b""
        self._send("stream on")
        self.streaming = True
        # 吃掉 hello 那一行，别让它混进样本。
        deadline = time.time() + 3
        while time.time() < deadline:
            chunk = self._serial.read(1, 0.3)
            if not chunk:
                continue
            self._buffer += chunk
            if self._buffer.endswith(b"\n"):
                text, self._buffer = self._buffer.decode("utf-8", "replace").strip(), b""
                if '"type":"hello"' in text:
                    return True
        return False

    def stop(self):
        self._send("stream off")
        self.streaming = False

    def close(self):
        try:
            if self.streaming:
                self.stop()
        finally:
            self._serial.close()

    # ---- 数据 ----
    def samples(self, seconds=5.0):
        """产出 (设备时间微秒, 原始幅值 µV)，最多读 seconds 秒。"""
        if not self.streaming:
            self.start()
        end = time.time() + seconds
        while time.time() < end:
            chunk = self._serial.read(1, 0.2)
            if not chunk:
                continue
            self._buffer += chunk
            if not self._buffer.endswith(b"\n"):
                continue
            text, self._buffer = self._buffer.decode("utf-8", "replace").strip(), b""
            if '"type":"samples"' not in text:
                continue
            try:
                message = json.loads(text)
            except ValueError:
                continue
            for item in message.get("data", []):
                # [序号, 设备时间微秒, 原始幅值µV, 保留位]
                yield int(item[1]), float(item[2])

    def picks(self):
        """问一次最近的 P/S 候选。"""
        self._send("picks")
        out = []
        deadline = time.time() + 1.5
        while time.time() < deadline:
            chunk = self._serial.read(1, 0.2)
            if not chunk:
                continue
            self._buffer += chunk
            if not self._buffer.endswith(b"\n"):
                continue
            text, self._buffer = self._buffer.decode("utf-8", "replace").strip(), b""
            if '"type":"pick"' not in text:
                continue
            try:
                out.append(json.loads(text))
            except ValueError:
                pass
        return out


# ---- 分析小工具（孩子能看懂的版本）----

def peak(samples):
    """最大振幅（µV）。"""
    return max((abs(v) for _, v in samples), default=0.0)


def zero_crossings(samples):
    """过零次数，粗略代表振动快慢。"""
    count = 0
    previous = None
    for _, value in samples:
        if previous is not None and ((previous < 0 <= value) or (value < 0 <= previous)):
            count += 1
        previous = value
    return count


def waveform_text(samples, columns=64, rows=9):
    """把一段波形画成终端里的字符图，左旧右新。"""
    if not samples:
        return ""
    values = [v for _, v in samples]
    top = max(abs(v) for v in values) or 1.0
    step = max(1, len(values) // columns)
    grid = [[" "] * columns for _ in range(rows)]
    middle = rows // 2
    for c in range(columns):
        chunk = values[c * step:(c + 1) * step]
        if not chunk:
            break
        lo, hi = min(chunk), max(chunk)

        def row_of(v):
            r = int(middle - (v / top) * middle)
            return max(0, min(rows - 1, r))

        a, b = sorted((row_of(lo), row_of(hi)))
        for r in range(a, b + 1):
            grid[r][c] = "|" if a != b else "-"
    return "\n".join("".join(row) for row in grid)


def bars(values, width=48):
    """把一串数字画成字符柱状图，终端里直接看。"""
    if not values:
        return ""
    top = max(abs(v) for v in values) or 1
    lines = []
    for v in values:
        n = int(abs(v) / top * width)
        lines.append(("+" if v >= 0 else "-") * max(n, 1))
    return "\n".join(lines)
