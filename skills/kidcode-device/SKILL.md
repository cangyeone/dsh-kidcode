---
name: kidcode-device
description: 地震仪屏幕的画图 API 全集：命令、坐标系、模拟器与真机的用法、常见故障。孩子要在屏幕上画东西、或命令被设备拒绝时读它。
whenToUse: 需要向地震仪发绘图命令、需要让模拟器出图、或 gfx 命令报错时
---

# 地震仪屏幕 API

## 屏幕

256 × 64 个格子，每个格子只有亮 / 灭。原点在左上角，y 向下增大。

```
(0,0) ─────────► x 255
  │
  ▼
 y 63
```

一帧 = 2048 字节 = 16384 个格子 = 256×64。

## 两条路，同一套命令

| 去处 | 怎么开 | 用途 |
|---|---|---|
| 模拟器 | `Board.simulate()` | 立刻出 PNG，不碰设备 |
| 真机 | `Board.connect()` | 屏幕真的亮起来 |

两边逐位一致（`tools/compare.py` 用画布哈希验证）。所以先模拟、后真机是安全的。

## Python 用法

```python
import sys; sys.path.insert(0, "tools")
import board

b = board.Board.simulate()
b.clear()
b.polyc(board.star())      # 五角星，居中，半径 21
b.show()
b.png("star.png", scale=4) # 给孩子看
print(b.hash())
```

真机只改一行：`b = board.Board.connect()`。

## 命令表

| 命令 | 参数 | 说明 |
|---|---|---|
| `clear` | — | 清空画布和文字，笔画计数归零 |
| `px` | x y | 一个点 |
| `line` | x1 y1 x2 y2 | 直线 |
| `rect` | x y w h | 空心方框 |
| `fill` | x y w h | 实心方框 |
| `circle` | cx cy r | 空心圆 |
| `poly` | x1 y1 x2 y2 … | 折线，最多 16 点 |
| `polyc` | … | 闭合折线（画星星用它） |
| `text` | x y 文字 | 写字（wqy12 字体，最多 31 字节） |
| `show` | — | 提交，回执带 ops |
| `overlay` | on / off | on=叠在波形上（默认） off=整屏只显示画 |
| `status` | — | 回执含 ops、texts、crc、age_ms |
| `dump` | [起始行] | 回 8 行的十六进制字节，用于核对 |

越界不报错：坐标会被裁剪或裁掉。只有语法错误才回 `{"ok":false,"error":…}`。

## 三条必须知道的规则

1. **主循环每 100 ms 重画整屏。** 所以画的东西放在叠加层，由固件在最后统一贴上去。`overlay off` 后如果 10 秒没有新命令，固件会自动回到波形——这是防卡死，不是故障。
2. **五角星要隔一个连。** 五个顶点相隔 72°，连接顺序是 0→2→4→1→3，否则画出来是五边形。`board.star()` 已经处理好。
3. **文字不进画布。** 文字由固件用字体单独绘制，`crc` 只覆盖像素。

## 校准与验收

```sh
python3 tools/compare.py                 # 10 组图形，模拟器 vs 真机
python3 tools/sim.py --out /tmp/a.png "gfx clear" "gfx polyc …" "gfx show"
```

`compare.py` 全绿才说明两边没分叉。改过固件的 `gfx.cpp` 或 `render.py` 之后必须重跑。

## 常见故障

| 现象 | 原因 | 处理 |
|---|---|---|
| 真机没反应 | 串口被别的程序占着 | 关掉其他串口工具 |
| 第一条命令丢失 | 打开串口会让 ESP32 复位 | `Board.connect()` 已等开机 hello，不要自己省掉 |
| 报 `streaming` | 正在 `stream on` | 先 `stream off` |
| 屏幕停在画上 | `overlay off` 且 10 秒无命令 | 属于自动恢复；想立刻回波形就发 `overlay on` |
| 真机画的和模拟器不一样 | 两边代码分叉 | 跑 `tools/compare.py`，不要手改期望值 |

## 不要做

- 不改固件、不烧录、不擦除。要改固件请人来做。
- 不发设备没有的命令（例如 `print`）。
- 不把 `crc` 当成屏幕亮度的证据——它只证明画布字节一致，屏幕是否真的亮要看人或拍照。
