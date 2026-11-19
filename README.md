# 编程小课堂 · 一个少儿编程科普的 DSH 智能体

用一句话指挥一台真的地震仪画画，再一起读懂它的数据。

这是一个 [DeepSeek Harness](https://github.com/deepseek-ai/dsh) 组合包：装进你的 profile 后，
会话的预设列表里会多一个**编程小课堂**——少儿人格、精简工具集、两条课程线，以及一套
「先说清三个问题、再动手」的教学流程。

```
孩子：画个五角星
老师：先问三件事——画什么、多大、去哪。
      → 电脑上出图 → 孩子说"再大点" → 满意了发到真机
      → 地震仪屏幕上真的亮起来
```

---

## 两条课程线

| 线 | 教什么 | 需要什么 |
|---|---|---|
| **编程**（12 课） | 让屏幕听话：点 → 线 → 图形 → 数据 → 作品 | 模拟器即可；上真机需要带 `gfx` 的固件 |
| **地震科普**（8 课） | 震动 → 地震 → 检测，每课都读真机数据 | `stream`，官方发布固件就支持 |

20 节课的详细安排见 [课程表.md](./课程表.md)。
地震线第一课已经完整可用：[课程/地震-01-震动](./课程/地震-01-震动)。

**没有硬件也能上课**：编程线有完整模拟器（`tools/board.py` 的 `Board.simulate()`），
地震线可以用任何 WAV/CSV 数据替代。硬件（科普地震仪 V2）只是让"真的亮起来"这件事发生。

---

## 安装

### 准备工作

- macOS（Windows/Linux 未测试）
- DeepSeek Harness 桌面端或 CLI
- 可选：一台科普地震仪 V2（ESP32-C3）

### 方式一：插件管理器（推荐）

```sh
dsh plugin --profile kidcode add github:cangyeone/dsh-kidcode
```

然后把这个包加进 profile 的组合包列表：

```sh
open ~/.dsh/profiles/kidcode/package.json
```

```json
"bundles": [
  "@deepseek-ai/dsh-base",
  "@deepseek-ai/dsh-web-app",
  "@cangyeone/dsh-kidcode"
]
```

### 方式二：桌面端插件页

在 **插件 → 安装** 里填：

```
github:cangyeone/dsh-kidcode
```

### 方式三：本地开发

```sh
git clone https://github.com/cangyeone/dsh-kidcode
mkdir -p ~/.dsh/profiles/kidcode/node_modules/@cangyeone
ln -s "$PWD/dsh-kidcode" ~/.dsh/profiles/kidcode/node_modules/@cangyeone/dsh-kidcode
```

### 启动

```sh
dsh kidcode --port 5050
```

浏览器打开它打印的地址，工作区选这个仓库目录，模式选**编程小课堂**。

工作区必须选仓库目录：`AGENTS.md`（设备速查）是按工作区加载的，
`课程/` 和 `tools/` 也都在里面。

---

## 它长什么样

- **首页**：进入模式就能看到两条课程线的卡片，点一课直接开始
- **会话里**：`对话 / 轨迹 / 课程` 三个页签，「课程」页签是大纲，随时可以翻
- **每个动作都有确认**：画什么 → 多大 → 去哪，每一步都带数字和后果

---

## 目录

| 路径 | 内容 |
|---|---|
| `AGENTS.md` | 自动进入对话前文的设备速查（改 agent 行为先改这里） |
| `课程表.md` | 20 节课与进度 |
| `课程/` | 每课：讲义、可运行 demo、一句话结论、家长话 |
| `skills/` | 三个 skill：怎么写课、怎么画图、怎么带孩子确认 |
| `tools/board.py` | 画笔：`Board.simulate()` / `Board.connect()` |
| `tools/seismo.py` | 读真机振动数据，纯标准库 |
| `tools/compare.py` | 验证模拟器与真机逐位一致 |
| `cordis.patch.yml` | 预设（人格 + 工具裁剪）与界面插件声明 |

---

## 硬件

科普地震仪 V2（ESP32-C3，256×64 单色屏，ADS1115 采样，板上跑 P/S 拾取模型）。

- 固件：[cangyeone/ustcshake-lppnm-firmware](https://github.com/cangyeone/ustcshake-lppnm-firmware)
- 编程线的画图命令（`gfx`）需要该仓库的 `v2.1.0-gfx` 分支/版本
- 地震线用官方发布版固件即可

设备不在身边时，编程线全程可用模拟器，地震线可用录好的数据。

---

## 卸载

```sh
rm -rf ~/.dsh/profiles/kidcode
```

不碰 DSH 安装，不碰其他 profile。

---

## 许可

MIT。上游模型（LPPNM）与固件另见各自仓库的许可说明。
