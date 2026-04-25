#!/bin/bash

# 実行ディレクトリへ移動
cd "/Users/imamichifumitaka/money-tools/tedori_dotcom"

# 実行ログの記録先
LOGFILE="/Users/imamichifumitaka/money-tools/tedori_dotcom/bot.log"
echo "--- Execution Started at $(date) ---" >> "$LOGFILE"

# ランダムな遅延（Jitter）を追加（1分〜45分: 60秒〜2700秒）
JITTER=$((60 + RANDOM % 2640))
echo "Sleeping for $JITTER seconds to avoid exact minute execution..." >> "$LOGFILE"
sleep $JITTER

# Homebrew等のpython3が使われる可能性があるため、通常パスを指定（環境に応じてフルパス推奨だが今回は/usr/bin/envで）
/usr/bin/env python3 auto_x_poster.py >> "$LOGFILE" 2>&1

echo "--- Execution Finished at $(date) ---" >> "$LOGFILE"
