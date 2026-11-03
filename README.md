# zero-basics-tutor（零基础教学）

一个通用的教学 skill：把学习者当作对当前主题完全没有基础的人，从能理解的起点一直讲到学习目标。学习者只需要读，不需要答。适用于任何领域，编程、数学、金融、法律、医学常识都可以。

遵循开放的 [Agent Skills](https://agentskills.io) 格式，Claude（Claude Code、claude.ai、API）、ChatGPT 和 Codex 都能使用。

## 它会怎样教

- **主动解释每个可能陌生的词。** 新词第一次出现时就地解释，解释不循环；类比要写明和真实情况的差别。
- **不考查。** 不问“懂了吗”，不要求作答、复述或动手操作，也不以学习者的反馈作为继续讲的条件。全文除了思考题题干，不出现问号。
- **思考题附答案。** 每道思考题在同一条回复里依次给出题目、分析和答案。
- **讲完整个流程。** 第一轮说明终点和路线，并讲到主题本身；之后每轮推进一段，用进度行收尾。
- **先检查再发送。** 每轮先写完整候选稿，用 `check_lesson.py` 做形式检查，再按 9 项审阅，最后发送。

## 按资料做学习文档

给它课件、讲义或其他资料，要求做成学习文档时：

- **每个文件都按上面的规则写**，单独检查。前面文件解释过的词记在词表里，后面的文件沿用同一个叫法。
- **引用资料时直接放进文档。** 提到资料里的图，就嵌入图片；提到原话、表格或代码，就把原文贴进来再讲解，学习者不需要再翻原资料。
- **多个文件时分步交给子会话。** 主会话负责拆分、检查和交接记录，每个文件交给一个新开的子会话写，避免上下文太长导致规则守不住。没有子会话功能的平台（例如 ChatGPT），就在同一个对话里逐个文件写、逐个检查。

## 目录结构

```
zero-basics-tutor/
├── SKILL.md                    # skill 正文（必需）
├── references/
│   ├── example-lesson.md       # 合格输出示范与反例，首次启用时读取
│   ├── release-review.md       # 连续记录格式和 9 项内容审阅
│   └── multi-step-documents.md # 分步做多份学习文档：交接记录、词表、子会话任务模板、验收步骤
├── scripts/
│   ├── check_lesson.py         # 检查候选稿中的形式问题（只需 Python 标准库）
│   ├── pdf_outline.py          # 列出 PDF 每页的标题、文字量和需要看图的页，并可把这些页存成图片
│   └── test_check_lesson.py    # 检查器自身的测试
├── agents/
│   └── openai.yaml             # ChatGPT / Codex 的显示名和默认提示词
├── evals/
│   └── evals.json              # 测试请求和核对标准（只用于测试，不需要安装）
└── README.md
```

## 安装和使用

### Claude Code

把整个文件夹放到 skills 目录下，**文件夹名必须是 `zero-basics-tutor`**，与 SKILL.md 中的 `name` 一致：

```bash
git clone https://github.com/Fingxing2025/zero-basics-tutor.git ~/.claude/skills/zero-basics-tutor
```

只在某个项目里用时，放到 `<项目>/.claude/skills/zero-basics-tutor/`。

使用时直接说“从零教我……”“我是小白，给我讲讲……”“按这份资料给我做学习文档”，Claude 会自动启用；也可以输入 `/zero-basics-tutor 主题名` 手动启用。

### Claude 网页版和桌面版（claude.ai）

1. 按下文“打包成 zip”做出 `zero-basics-tutor.zip`。
2. 在设置里找到“技能（Skills）”，上传这个 zip 并启用。
3. 在对话中用自然语言提出学习请求。

### Claude API

通过 Skills API 上传同一个文件夹，在请求中引用这个 skill。

### ChatGPT

ChatGPT 的 Skills 功能使用同样的 SKILL.md 格式。是否可用取决于你的套餐；在工作区里，可能需要管理员先在设置里开启 Skills 和上传权限。

1. 按下文“打包成 zip”做出 `zero-basics-tutor.zip`。
2. 在侧边栏打开 **Skills**，选择创建，再选择从电脑上传，上传这个 zip。上传后 ChatGPT 会先扫描，通常扫描完成后即可使用。
3. 提出学习请求时，ChatGPT 会自动选用；也可以输入 `@` 选择“零基础教学”。

在 ChatGPT 上使用时：

- 运行检查脚本需要 ChatGPT 能执行代码。不能执行时，skill 会按同样的项目直接审阅文本，并说明脚本没有运行。
- ChatGPT 没有子会话，多份学习文档会在同一个对话里逐个写、逐个检查。文件很多时，建议分几次对话完成，每次做几份。
- `pdf_outline.py` 需要 poppler。环境里没有时，skill 会改用已有的 PDF 工具，例如 PyMuPDF 或 pypdf。
- 学习文档以下载文件交付时，文档和 `图片/` 文件夹会打包成一个 zip，解压后图片才能正常显示。

**套餐里没有 Skills 时**，可以用“项目”（Projects）或自定义 GPT 代替：把 `SKILL.md` 和 `references/` 里的三个文件作为文件上传，在指令里写：

```text
本项目的全部教学按上传文件中的 SKILL.md 执行（零基础教学），并按它的要求阅读 example-lesson.md、release-review.md 和 multi-step-documents.md。
```

这种方式下，模型需要自己去读这些文件，触发和执行都不如 Skills 稳定；`scripts/` 里的脚本也只能在可以执行代码时使用。

### Codex

Codex 从 `~/.agents/skills`（个人）或仓库里的 `.agents/skills`（项目）读取 skill：

```bash
git clone https://github.com/Fingxing2025/zero-basics-tutor.git ~/.agents/skills/zero-basics-tutor
```

用 `$zero-basics-tutor` 调用，或者直接提出学习请求，让 Codex 自动选用。`agents/openai.yaml` 提供显示名和默认提示词。

## 打包成 zip

上传到 claude.ai 或 ChatGPT 时，需要一个只含 skill 文件、顶层文件夹名为 `zero-basics-tutor` 的 zip。在仓库根目录运行：

```bash
git archive --format=zip --prefix=zero-basics-tutor/ -o zero-basics-tutor.zip HEAD SKILL.md agents references scripts
```

这个命令打包的是最近一次提交的内容，未提交的修改不会包含进去。

## 依赖

- **Python 3.9 或更高版本**：运行两个脚本。`check_lesson.py` 只用标准库。
- **poppler**（可选）：`pdf_outline.py` 需要其中的 `pdftotext`、`pdfimages`、`pdfinfo` 和 `pdftoppm`。macOS 上用 `brew install poppler` 安装。

## 检查与测试

```bash
python3 scripts/check_lesson.py /绝对路径/draft.md
python3 scripts/test_check_lesson.py
python3 scripts/pdf_outline.py --images 学习文档/图片 资料.pdf
```

`check_lesson.py` 的退出码：

| 退出码 | 含义 |
|---|---|
| 0 | 没有发现脚本覆盖的形式问题 |
| 1 | 发现了问题 |
| 2 | 输入或执行失败 |

`check_lesson.py` 检查以下形式问题：
- 固定的禁用措辞；
- 思考题题干之外的问号；
- 思考题的标签、内容和顺序；
- 代码围栏；
- 末尾的进度行；
- 嵌入的图片能否打开。

它会跳过 `<!-- 原文 -->` 和 `<!-- /原文 -->` 之间的资料原文摘录。报告中的 `draft_sha256` 用来识别检查的是哪一版文本；`semantic_compliance: not_assessed` 表示脚本没有评估内容含义，内容要按 `references/release-review.md` 另外审阅。

`evals/evals.json` 包含 5 个测试请求，每个附有可以逐条核对的标准。修改 SKILL.md 后，建议用这些请求比较新旧版本的输出。记录时写明模型、请求、实际输出和逐项结果，尽量覆盖“继续”“不懂”“跳过”“暂停恢复”、长对话和含代码公式的场景；没有实际运行就标明未测试，不填写遵循率。

## 能力边界

这些流程能减少遗漏，但不能保证模型百分之百遵循。

- skill 本身不能拦截聊天输出。只有外部应用实际接入“生成草稿—检查—修改—批准后展示”的流程，才能在展示前由程序阻止检查失败的稿件。
- 检查器测试通过，不等于教学效果或多轮对话测试通过。
- 按资料做的学习文档包含资料原文和图片，适合个人学习，不适合公开发布。
