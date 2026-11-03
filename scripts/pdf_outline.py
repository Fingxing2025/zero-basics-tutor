#!/usr/bin/env python3
"""列出 PDF 每一页的标题、文字量和插图数，标出需要看图的页。

用法：python3 scripts/pdf_outline.py 资料1.pdf [资料2.pdf ...]

主会话用它规划分步，不必把资料全文和图片读进上下文。
需要 poppler 的 pdftotext 和 pdfimages（macOS：brew install poppler）。

某页满足下面任一条件，就标为“看图”：
- 有插图（在一半以上页面重复出现、尺寸相同的图片算装饰，例如校徽，不计入）；
- 提取出的文字少于 80 个字符（多半是截图或整页图片）。
"""

import collections
import shutil
import subprocess
import sys

MIN_TEXT = 80


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def outline(path):
    pages = run("pdftotext", "-layout", path, "-").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()

    # pdfimages -list 的列：page num type width height ...
    sizes = collections.defaultdict(list)
    for line in run("pdfimages", "-list", path).splitlines()[2:]:
        cols = line.split()
        if len(cols) > 4 and cols[2] == "image":
            sizes[int(cols[0])].append((cols[3], cols[4]))
    pages_with = collections.Counter(s for page in sizes.values() for s in set(page))
    decoration = {s for s, n in pages_with.items() if n > len(pages) / 2}

    print(f"== {path}（{len(pages)} 页）")
    print("页 | 文字字符 | 插图 | 看图 | 标题")
    marked = []
    for no, text in enumerate(pages, 1):
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        title = lines[0][:60] if lines else "（无文字）"
        chars = sum(len(l) for l in lines)
        images = sum(1 for s in sizes.get(no, []) if s not in decoration)
        need = images > 0 or chars < MIN_TEXT
        if need:
            marked.append(no)
        print(f"{no} | {chars} | {images} | {'是' if need else ''} | {title}")
    print(f"需要看图的页：{', '.join(map(str, marked)) or '无'}")


def main(paths):
    if not paths:
        print(__doc__.strip())
        return 2
    missing = [t for t in ("pdftotext", "pdfimages") if not shutil.which(t)]
    if missing:
        print(f"缺少 {'、'.join(missing)}，请先安装 poppler。")
        return 2
    for path in paths:
        outline(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
