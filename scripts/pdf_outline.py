#!/usr/bin/env python3
"""列出 PDF 每一页的标题、文字量和插图数，标出需要看图的页；可以把这些页存成图片，供学习文档嵌入。

用法：
  python3 scripts/pdf_outline.py 资料1.pdf [资料2.pdf ...]
  python3 scripts/pdf_outline.py --images 学习文档/图片 资料1.pdf [资料2.pdf ...]
  python3 scripts/pdf_outline.py --images 学习文档/图片 --pages 16,17 资料1.pdf

第一种只列目录。第二种同时把标为“看图”的页存成 PNG 图片。第三种不列目录，只把指定的页存成图片，
用于补存没有被标出、但讲解时要引用的页。图片名是“资料文件名-p页码.png”，例如 lesson3-processes-p08.png。

主会话用它规划分步，不必把资料全文和图片读进上下文。
需要 poppler 的 pdftotext、pdfimages、pdfinfo 和 pdftoppm（macOS：brew install poppler）。

某页满足下面任一条件，就标为“看图”：
- 有插图（在一半以上页面重复出现、尺寸相同的图片算装饰，例如校徽，不计入）；
- 提取出的文字少于 80 个字符（多半是截图或整页图片）。
用线条画成的图（例如课件里直接画的甘特图）不算插图，可能没被标出，需要时用 --pages 补存。
"""

import argparse
import collections
import re
import shutil
import subprocess
import sys
from pathlib import Path

MIN_TEXT = 80
DPI = 150
TOOLS = ("pdftotext", "pdfimages", "pdfinfo", "pdftoppm")


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def page_count(path):
    return int(re.search(r"^Pages:\s+(\d+)", run("pdfinfo", path), re.MULTILINE)[1])


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
    return marked


def render(path, numbers, folder):
    total = page_count(path)
    width = max(2, len(str(total)))
    folder.mkdir(parents=True, exist_ok=True)
    for no in numbers:
        if not 1 <= no <= total:
            print(f"跳过第 {no} 页：{path} 只有 {total} 页。")
            continue
        out = folder / f"{Path(path).stem}-p{no:0{width}d}"
        run("pdftoppm", "-r", str(DPI), "-png", "-f", str(no), "-l", str(no), "-singlefile", path, str(out))
        print(f"第 {no} 页 → {out}.png")


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdfs", nargs="+", help="PDF 资料")
    parser.add_argument("--images", type=Path, help="把页面存成图片的目录，通常是学习文档旁边的 图片/")
    parser.add_argument("--pages", help="只存这些页，用逗号分隔，例如 16,17；只能配合一份 PDF 使用")
    args = parser.parse_args(argv)
    if args.pages and (not args.images or len(args.pdfs) > 1):
        parser.error("--pages 需要配合 --images，并且只能给一份 PDF。")
    missing = [t for t in TOOLS if not shutil.which(t)]
    if missing:
        print(f"缺少 {'、'.join(missing)}，请先安装 poppler。")
        return 2
    if args.pages:
        render(args.pdfs[0], [int(n) for n in args.pages.split(",") if n.strip()], args.images)
        return 0
    for path in args.pdfs:
        marked = outline(path)
        if args.images:
            render(path, marked, args.images)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
