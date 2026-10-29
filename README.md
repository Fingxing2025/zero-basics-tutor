# zero-basics-tutor（零基础教学）

这是一个通用的教学 skill。它把学习者当作对当前主题完全没有基础的人，从能理解的起点一直完整讲到学习目标：

- 主动解释每个可能陌生的词，解释不循环；
- 不出题考查，不问“懂了吗”，不以学习者的反馈作为继续讲的条件；
- 思考题在同一条回复里直接给出分析和答案；
- 分阶段讲完整个流程，每轮以进度行收尾。

## 目录结构

```
zero-basics-tutor/
├── SKILL.md                    # skill 正文（必需）
├── references/
│   ├── example-lesson.md       # 合格输出示范与反例，首次启用时读取
│   └── release-review.md       # 内容审阅、连续记录和检查能力边界
├── scripts/
│   ├── check_lesson.py         # 检查候选稿中的已覆盖形式问题
│   └── test_check_lesson.py    # 检查器自身测试，不是模型遵循率测试
├── agents/
│   └── openai.yaml             # Codex / OpenAI 智能体的界面配置
├── evals/
│   └── evals.json              # 测试用例（只用于测试，不需要安装）
└── README.md
```

## 在 Claude 中使用

### Claude Code

把整个文件夹放到 skills 目录下，**文件夹名必须是 `zero-basics-tutor`**，与 SKILL.md 中的 `name` 一致：

- 只给自己用：`~/.claude/skills/zero-basics-tutor/`
- 只在某个项目里用：`<项目>/.claude/skills/zero-basics-tutor/`

```bash
git clone https://github.com/Fingxing2025/zero-basics-tutor.git ~/.claude/skills/zero-basics-tutor
```

使用方法：

- 直接说“从零教我……”“我是小白，给我讲讲……”，Claude 会自动启用这个 skill；
- 或者输入 `/zero-basics-tutor 主题名`，手动启用。

### Claude 网页版 / 桌面版（claude.ai）

1. 把 `SKILL.md`、`references/`、`scripts/`、`agents/` 放进一个名为 `zero-basics-tutor` 的文件夹，然后把这个文件夹压缩成 zip。也可以把这个文件夹打包成 `zero-basics-tutor.skill` 文件，它本身就是 zip 格式。
2. 在设置中找到“技能（Skills）”，上传这个压缩包并启用。
3. 在对话中用自然语言提出学习请求即可。

### Claude API

通过 Skills API 上传同一个文件夹，在请求中引用这个 skill 即可。

## 在 Codex / OpenAI 智能体中使用

`agents/openai.yaml` 提供显示名称和默认提示词，可以用 `$zero-basics-tutor` 调用。

## 测试

`evals/evals.json` 包含 3 个测试请求，每个请求附有可以逐条核对的检查项，例如：是否就地解释了陌生词、思考题是否附有答案、结尾是否没有提问。修改 SKILL.md 后，建议用这些测试请求检查新旧两个版本的输出。

候选讲义的形式检查只需要 Python 3 标准库：

```bash
python3 scripts/check_lesson.py /绝对路径/draft.md
python3 scripts/test_check_lesson.py
```

退出码 0 表示没有发现当前脚本覆盖的形式问题；1 表示有发现；2 表示输入或执行失败。报告中的 `draft_sha256` 是识别所检查文本的摘要，正文一旦变化就需要重查。`semantic_compliance: not_assessed` 表示脚本没有评估内容含义。完整执行流程还需要按照 `references/release-review.md` 审阅概念、解释顺序、例子和进度。没有工具时只能进行文本审阅，不得声称自动检查已执行。

这些流程能帮助减少遗漏，不能保证模型百分之百遵循。当前文件本身不能拦截聊天输出；需要外部应用实际接入检查流程，才能在展示前由程序阻止检查失败的稿件。检查器测试通过不等于教学效果或多轮模型测试通过。
