# zero-basics-tutor（零基础教学）

给“这门课平时没学、考前要临时学会”的人用的教学 skill。也能用来学新东西。

核心做法：**从一个具体问题进去，只补这个问题用到的知识，配图讲清，把问题解出来。**

- **讲卷子：** 一题一节，结构是“原题 → 要用到的知识 → 一步步解 → 答案（对照参考答案）”。
- **按课件做学习文档：** 一章一份，分两部分。“会考的内容”是本章地图 → 沿着 3～6 道典型题讲 → 一页速记卡；“剩下的部分”按课件顺序逐条简写其余内容，保证每一页都有去向。
- **学新东西：** 由浅入深排几个具体问题，每个问题只比上一个多一个难点。
- **中途追问：** 直接在聊天里回答，不走额外流程。
- **配图：** 精确的图（时间线、波形、受力图）用 matplotlib 或 Graphviz 画，示意插画用生图模型画，复杂过程拆成一组逐步变化的图。
- **零基础：** 陌生词第一次出现时就地解释，只讲到能看懂这一处为止。

## 怎么用

只有点名才会启用：

> 用零基础教学skill讲一下 `大学物理C卷子/2024-2025学年下学期期末.md`

说“从零教我”“我是小白”不会触发。

## 依赖

| 用途 | 需要 |
|---|---|
| 精确图 | [uv](https://docs.astral.sh/uv/)（自动临时安装 matplotlib）、Noto Sans CJK 字体 |
| 流程图、状态图、本章地图 | Graphviz（`dot`） |
| 读课件 PDF、截原图 | poppler（`pdftotext`、`pdftoppm`） |
| 示意插画 | 一个 OpenAI 兼容的生图接口 |

配置生图接口：运行下面的命令，按提示粘贴 key（输入时不显示）。配置存进 `~/.config/zero-basics-tutor/env`，权限为只有自己能读。

```bash
bash ~/.claude/skills/zero-basics-tutor/scripts/set_key.sh [接口地址] [模型]
```

默认接口是 `https://api.supergpt.dev/v1`，默认模型是 `gpt-image-2.6-sunburst`。也可以用同名环境变量 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`IMAGE_MODEL` 覆盖。

## 目录

```
zero-basics-tutor/
├── SKILL.md              # skill 正文
├── scripts/gen_image.py  # 调用生图接口画一张图（只用 Python 标准库）
├── scripts/set_key.sh    # 不回显地保存生图 key
├── agents/openai.yaml    # ChatGPT / Codex 的显示名和默认提示词
└── evals/evals.json      # 测试用例
```

## 安装

```bash
git clone https://github.com/Fingxing2025/zero-basics-tutor.git ~/.claude/skills/zero-basics-tutor
```

Codex 放到 `~/.agents/skills/zero-basics-tutor`。
