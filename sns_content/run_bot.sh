#!/bin/zsh
export PATH="/Users/imamichifumitaka/Library/Python/3.9/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export PYTHONPATH="/Users/imamichifumitaka/Library/Python/3.9/lib/python/site-packages:$PYTHONPATH"

export TWITTER_API_KEY="UHvEB9eE3lyWM4zPARambujIa"
export TWITTER_API_SECRET="VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn"
export TWITTER_ACCESS_TOKEN="1924677045784838144-hrHWl35Sim0p9PW5WUUSaXYUzUW1n0"
export TWITTER_ACCESS_SECRET="Vs1qPPGRMtyRU9sacMBqA59ppnMrNZLe9iWDvoiTtRpf6"

DIR="/Users/imamichifumitaka/Downloads/ミカタ_経理/今道_生活を豊かに/money-tools"
LOG="$DIR/sns_content/bot.log"
cd "$DIR"

# Botだと悟られないよう、最大45分（2700秒）のランダムな待機時間を設ける
RANDOM_DELAY=$((RANDOM % 2700))
echo "--- 🚀 Starting High-Engagement Bot Sequence at $(date) - Waiting for ${RANDOM_DELAY}s... ---" >> "$LOG"
sleep $RANDOM_DELAY

# 1. 絶望・ブックマーク特化型メイン投稿 (URLなし)
echo "[$(date)] Executing Auto X Poster (No URLs)..." >> "$LOG"
python3 "$DIR/auto_x_poster.py" >> "$LOG" 2>&1

# 2. ツイート成果の自己評価（PDCAエンジン） - ブックマーク重視
echo "[$(date)] Executing SNS PDCA Evaluator..." >> "$LOG"
python3 "$DIR/sns_pdca_evaluator.py" >> "$LOG" 2>&1

echo "--- ✅ Sequence Completed at $(date) ---" >> "$LOG"
