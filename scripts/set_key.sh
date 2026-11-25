#!/usr/bin/env bash
# Save the image API key to ~/.config/zero-basics-tutor/env without echoing it.
# Usage: bash set_key.sh [base_url] [model]
set -euo pipefail
cfg_dir="$HOME/.config/zero-basics-tutor"
cfg="$cfg_dir/env"
base="${1:-https://api.supergpt.dev/v1}"
model="${2:-gpt-image-2.6-sunburst}"

read -rsp "粘贴生图 API key 后按回车（输入不会显示）: " key
echo
if [ -z "$key" ]; then
  echo "没有输入 key，未做修改。" >&2
  exit 1
fi

mkdir -p "$cfg_dir"
umask 077
cat > "$cfg" <<EOF
OPENAI_API_KEY=$key
OPENAI_BASE_URL=$base
IMAGE_MODEL=$model
EOF
chmod 600 "$cfg"
echo "已保存到 $cfg（只有你自己能读）。接口：$base，模型：$model"
