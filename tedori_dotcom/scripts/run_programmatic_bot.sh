#!/bin/bash
# ---------------------------------------------------------
# tedori-keisan.com API不要・自律型プログラマティックSEOBot 実行ラッパー
# ---------------------------------------------------------

# プロジェクトディレクトリへ移動
cd /Users/imamichifumitaka/money-tools/tedori_dotcom

# 環境変数の読み込み (ログインユーザーの環境を再現)
source ~/.zshrc

# Pythonスクリプトの実行
/usr/bin/python3 scripts/programmatic_seo_bot.py >> /Users/imamichifumitaka/money-tools/tedori_dotcom/scripts/programmatic_bot.log 2>&1
