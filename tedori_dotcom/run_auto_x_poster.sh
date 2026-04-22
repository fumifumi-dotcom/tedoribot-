#!/bin/bash

# 実行ディレクトリへ移動
cd "/Users/imamichifumitaka/Downloads/生活を豊かに/money-tools/tedori_dotcom"

# 実行ログの記録先
LOGFILE="/Users/imamichifumitaka/Downloads/生活を豊かに/money-tools/tedori_dotcom/bot.log"
echo "--- Execution Started at $(date) ---" >> "$LOGFILE"

# Homebrew等のpython3が使われる可能性があるため、通常パスを指定（環境に応じてフルパス推奨だが今回は/usr/bin/envで）
/usr/bin/env python3 auto_x_poster.py >> "$LOGFILE" 2>&1

echo "--- Execution Finished at $(date) ---" >> "$LOGFILE"
