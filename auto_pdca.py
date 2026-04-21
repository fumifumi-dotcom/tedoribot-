import os
import json
import tweepy
import time
from datetime import datetime

# API鍵の設定
API_KEY = "UHvEB9eE3lyWM4zPARambujIa"
API_SECRET = "VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn"
ACCESS_TOKEN = "1924677045784838144-hrHWl35Sim0p9PW5WUUSaXYUzUW1n0"
ACCESS_SECRET = "Vs1qPPGRMtyRU9sacMBqA59ppnMrNZLe9iWDvoiTtRpf6"

def run_pdca():
    print(f"--- [PDCA Auto-Optimizer] Started at {datetime.now()} ---")
    
    client = tweepy.Client(
        consumer_key=API_KEY, consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET
    )
    
    history_file = 'sns_content/tweet_history.json'
    db_file = 'sns_content/templates.json'
    
    if not os.path.exists(history_file) or not os.path.exists(db_file):
        print("Required files not found. Exiting.")
        return
        
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
        
    with open(db_file, 'r', encoding='utf-8') as f:
        templates = json.load(f)
        
    # 最新の50件を取得（TwitterAPIの制限考慮）
    recent_history = history[-50:]
    if not recent_history:
        print("No history to evaluate.")
        return
        
    tweet_ids = [str(item['tweet_id']) for item in recent_history]
    
    try:
        # 100件まで一度に取得可能
        response = client.get_tweets(ids=tweet_ids, tweet_fields=["public_metrics"])
        if not response.data:
            print("Could not fetch tweet metrics from API.")
            return
            
        metrics_map = {str(t.id): t.public_metrics for t in response.data}
    except Exception as e:
        print(f"API Error fetching metrics: {e}")
        return
        
    # テンプレートごとの成績集計
    template_performance = {}
    for item in recent_history:
        tid = str(item['tweet_id'])
        tpl_id = item['template_id']
        
        if tid in metrics_map:
            m = metrics_map[tid]
            # KPI算出ロジック: いいね=1点, RT=3点, リプライ=2点, ブックマーク=2点
            engagement = m.get('like_count', 0) * 1.0 + \
                         m.get('retweet_count', 0) * 3.0 + \
                         m.get('reply_count', 0) * 2.0 + \
                         m.get('bookmark_count', 0) * 2.0
            
            if tpl_id not in template_performance:
                template_performance[tpl_id] = {'total_eng': 0, 'count': 0}
            template_performance[tpl_id]['total_eng'] += engagement
            template_performance[tpl_id]['count'] += 1
            
    # スコア（重み）の自然淘汰アップデート
    print("\n[Template Performance Update]")
    for tpl in templates:
        tid = tpl['id']
        old_score = tpl.get('score', 10.0)
        
        if tid in template_performance:
            avg_eng = template_performance[tid]['total_eng'] / template_performance[tid]['count']
            
            # 学習係数: エンゲージメントがあればスコアを上げる、なければ少し減衰する（陳腐化防止）
            if avg_eng > 0:
                new_score = old_score + (avg_eng * 1.5)
                print(f"🔼 {tid} | Avg Eng: {avg_eng:.1f} | Score: {old_score:.1f} -> {new_score:.1f}")
            else:
                new_score = old_score * 0.95 # 5%減衰
                print(f"🔻 {tid} | Avg Eng: {avg_eng:.1f} | Score: {old_score:.1f} -> {new_score:.1f}")
                
            tpl['score'] = min(max(new_score, 1.0), 100.0) # Cap score between 1.0 and 100.0
        else:
            # まだ使われていない場合はスコア維持
            print(f"➖ {tid} | Unused | Score: {old_score:.1f}")

    # 保存
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(templates, f, indent=2, ensure_ascii=False)
        
    print("\n--- [PDCA Auto-Optimizer] Completed successfully. Templates Database updated. ---")

if __name__ == '__main__':
    run_pdca()
