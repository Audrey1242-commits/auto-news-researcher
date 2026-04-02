import os
import time
from datetime import datetime, timedelta
from google import genai

# ===== 設定（GitHub Secretsから読み込み） =====
# ローカルでテストする場合は環境変数に設定してください
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
LINE_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("USER_ID")

# ===== クライアント初期化 =====
client = genai.Client(api_key=GEMINI_API_KEY)

# ===== 日付生成 =====
today = datetime.now()
past = today - timedelta(days=7)
date_range = f"{past.strftime('%Y年%m月%d日')}〜{today.strftime('%Y年%m月%d日')}"

# ===== Deep Research実行関数 =====
def run_deep_research(prompt):
    # Deep Researchを有効化して実行
    interaction = client.interactions.create(
        model="gemini-2.0-flash", # Deep Research対応モデル
        input=prompt,
        config={
            "tools": [{"google_search_retrieval": {}}], # 検索ツールを有効化
        }
    )
    
    print(f"リサーチ開始 (ID: {interaction.id})")

    # 完了まで待機（ポーリング）
    while True:
        status = client.interactions.get(interaction.id)
        if status.state == "COMPLETED":
            return status.result.text
        elif status.state == "FAILED":
            raise Exception(f"Deep Research失敗: {status.error}")
        
        print("調査中...")
        time.sleep(20) # 20秒待機

# ===== LINE送信関数 =====
import requests
def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message[:4900]}]
    }
    requests.post(url, headers=headers, json=body)

# ===== メイン処理 =====
prompts = [
    f"{date_range}の日本および世界の「経済・国際情勢・政治」に関する主要ニュースをリサーチし、詳細レポートを作成して。",
    f"{date_range}の「AI・半導体・ITサービス」に関する最新ニュースとビジネストレンドをリサーチして。",
    f"{date_range}の日本株・米国株における、現在の市場環境で注目すべき銘柄とその理由をリサーチして。"
]

if __name__ == "__main__":
    for i, p in enumerate(prompts, 1):
        print(f"--- 質問{i}を実行中 ---")
        try:
            result = run_deep_research(p)
            send_line(f"【質問{i}のリサーチ結果】\n\n{result}")
        except Exception as e:
            print(f"エラー: {e}")
            send_line(f"【質問{i}】リサーチ中にエラーが発生しました。")
