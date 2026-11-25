#!/usr/bin/env python3
"""Generate one illustration with an OpenAI-compatible image API and save it as PNG.

Only the Python standard library is used. Configuration comes from environment
variables, or, for any that are unset, from the file ~/.config/zero-basics-tutor/env
(KEY=VALUE lines), so the API key never appears on the command line or in chat:

  OPENAI_API_KEY   required
  OPENAI_BASE_URL  optional, e.g. https://example.com/v1 (default: https://api.openai.com/v1)
  IMAGE_MODEL      optional, default gpt-image-2.6-sunburst

Example:
  python3 gen_image.py "多个人排队等一台咖啡机，扁平插画风格，不要任何文字" -o 图片/排队.png
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_MODEL = "gpt-image-2.6-sunburst"
DEFAULT_BASE = "https://api.openai.com/v1"
# Some gateways (Cloudflare) reject the default "Python-urllib" User-Agent.
USER_AGENT = "zero-basics-tutor/1.0"
CONFIG_FILE = os.path.expanduser("~/.config/zero-basics-tutor/env")


def load_config_file() -> None:
    """Fill unset environment variables from CONFIG_FILE, if it exists."""
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                name = name.strip().removeprefix("export ").strip()
                value = value.strip().strip("'\"")
                if value and not os.environ.get(name):
                    os.environ[name] = value
    except FileNotFoundError:
        pass


def main() -> int:
    load_config_file()
    p = argparse.ArgumentParser(description="用生图模型画一张示意插画，存成 PNG。")
    p.add_argument("prompt", help="画面描述。建议写明“不要任何文字”。")
    p.add_argument("-o", "--out", required=True, help="输出图片路径，例如 图片/排队.png")
    p.add_argument("--size", default="1024x1024",
                   help="尺寸，如 1024x1024、1536x1024、1024x1536（默认 1024x1024）")
    p.add_argument("--quality", help="可选：low / medium / high；不填由服务端决定")
    p.add_argument("--model", default=os.environ.get("IMAGE_MODEL", DEFAULT_MODEL),
                   help=f"模型 ID（默认取 IMAGE_MODEL 环境变量，否则 {DEFAULT_MODEL}）")
    p.add_argument("--timeout", type=int, default=300, help="请求超时秒数（默认 300）")
    args = p.parse_args()

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print(f"缺少 OPENAI_API_KEY（环境变量或 {CONFIG_FILE}）。"
              "请用户自己在终端设置，不要把 key 贴进聊天。", file=sys.stderr)
        return 2
    base = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE).rstrip("/")

    body = {"model": args.model, "prompt": args.prompt, "size": args.size, "n": 1}
    if args.quality:
        body["quality"] = args.quality

    req = urllib.request.Request(
        f"{base}/images/generations",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": USER_AGENT},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        print(f"接口返回 HTTP {e.code}：{detail}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"请求失败：{e}", file=sys.stderr)
        return 1

    try:
        item = data["data"][0]
    except (KeyError, IndexError, TypeError):
        print(f"返回内容里没有图片：{json.dumps(data, ensure_ascii=False)[:500]}", file=sys.stderr)
        return 1

    if item.get("b64_json"):
        image = base64.b64decode(item["b64_json"])
    elif item.get("url"):
        img_req = urllib.request.Request(item["url"], headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(img_req, timeout=args.timeout) as resp:
            image = resp.read()
    else:
        print("返回的图片既没有 b64_json 也没有 url。", file=sys.stderr)
        return 1

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "wb") as f:
        f.write(image)
    print(f"已保存 {args.out}（{len(image) // 1024} KB，模型 {args.model}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
