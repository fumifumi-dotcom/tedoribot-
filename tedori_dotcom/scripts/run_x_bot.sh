#!/bin/bash
cd "$(dirname "$0")"

# 仮想環境があれば有効化
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# 初回は対話モード（ターミナルから）で起動する
echo "=== X Parasite Bot ==="
echo "初回は手動でX (Twitter) にログインする必要があります。"
python3 x_parasite_bot.py
