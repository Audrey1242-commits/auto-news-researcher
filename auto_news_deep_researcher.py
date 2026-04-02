import os
import time
import requests
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# ===== 1. 設定 =====
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
LINE_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("USER_ID")

# クライアント初期化
client = genai.Client(api_key=GEMINI_API_KEY)

# ===== 2. 検索付きリサーチ関数 (安定版) =====
def run_stable_research(prompt):
    # Deep Research (Interactions) ではなく、
    # 通常の generate_content に Google検索ツールを載せます。
    # これなら URL 404 エラーは発生しません。
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    
    if not response.text:
        return "結果を取得できませんでした。"
    
    return response.text

# ===== 3. LINE送信関数 =====
def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}", "Content-Type": "application/json"}
    body = {"to": USER_ID, "messages": [{"type": "text", "text": message[:4900]}]}
    requests.post(url, headers=headers, json=body)

# ===== 4. メイン処理 =====
if __name__ == "__main__":
    today = datetime.now()
    date_range = f"{(today - timedelta(days=7)).strftime('%Y年%m月%d日')}〜{today.strftime('%Y年%m月%d日')}"
    
    prompts = [
        f"{date_range}の「経済・国際情勢」に関するニュースをGoogle検索を使って調査し、背景を含めて詳細に報告して。",
        f"{date_range}の「最新AI・ITトレンド」をGoogle検索を使って調査し、要約して。"
    ]

    for i, p in enumerate(prompts, 1):
        print(f"\n--- 質問{i}開始 ---")
        try:
            # 安定した「検索付き生成」を実行
            result = run_stable_research(p)
            send_line(f"【週刊リサーチ:{i}】\n\n{result}")
            print(f"質問{i} 完了")
        except Exception as e:
            print(f"エラー発生: {e}")
            send_line(f"エラー発生: {e}")
        
        time.sleep(5)
