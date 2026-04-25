#!/bin/bash
# ---------------------------------------------------------
# tedori-keisan.com 自律型コンテンツ生成Bot 実行ラッパー
# ---------------------------------------------------------

# プロジェクトディレクトリへ移動
cd /Users/imamichifumitaka/money-tools/tedori_dotcom

# 環境変数の読み込み (ログインユーザーの環境を再現)
source ~/.zshrc

# Pythonスクリプトの実行
/usr/bin/python3 scripts/autonomous_content_bot.py >> /Users/imamichifumitaka/money-tools/tedori_dotcom/scripts/bot_run.log 2>&1
