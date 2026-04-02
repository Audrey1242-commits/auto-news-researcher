import os
import time
import requests
from datetime import datetime, timedelta

# ===== 1. 設定 =====
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
LINE_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("USER_ID")

# ===== 2. Deep Research実行関数 =====
def run_deep_research(prompt):
    # 【最重要】Deep Researchが確実に動作するモデル名とエンドポイントの組み合わせ
    model_id = "gemini-2.0-flash" 
    base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    # 404を回避するためのパス形式
    create_url = f"{base_url}/models/{model_id}:createInteraction?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    body = {
        "input": prompt,
        "tools": [
            {
                "google_search_retrieval": {
                    "dynamic_retrieval_config": {
                        "mode": "MODE_UNSPECIFIED",
                        "dynamic_threshold": 0.06
                    }
                }
            }
        ]
    }

    print(f"Sending request to: {create_url}")
    response = requests.post(create_url, headers=headers, json=body)
    
    if response.status_code != 200:
        # ここでエラーが出る場合、APIキーが「Google AI Studio」でDeep Research権限を持っているか確認が必要です
        raise Exception(f"API起動エラー (Status: {response.status_code}): {response.text}")

    res_data = response.json()
    resource_name = res_data.get("name", "")
    interaction_id = resource_name.split("/")[-1]
    
    print(f"リサーチ開始成功 (ID: {interaction_id})")

    # ステータス確認
    status_url = f"{base_url}/interactions/{interaction_id}?key={GEMINI_API_KEY}"
    
    while True:
        status_res = requests.get(status_url)
        if status_res.status_code != 200:
            print(f"ステータス確認待ち... ({status_res.status_code})")
            time.sleep(20)
            continue

        status_data = status_res.json()
        state = status_data.get("state", "UNKNOWN")
        
        if state == "COMPLETED":
            return status_data.get("result", {}).get("text", "結果が取得できませんでした")
        elif state == "FAILED":
            raise Exception(f"リサーチ失敗: {status_data.get('error')}")
        
        print(f"調査中... (ステータス: {state})")
        time.sleep(30)

# ===== 3. LINE送信 / メイン処理 (変更なし) =====
def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}", "Content-Type": "application/json"}
    body = {"to": USER_ID, "messages": [{"type": "text", "text": message[:4900]}]}
    requests.post(url, headers=headers, json=body)

if __name__ == "__main__":
    today = datetime.now()
    date_range = f"{(today - timedelta(days=7)).strftime('%Y年%m月%d日')}〜{today.strftime('%Y年%m月%d日')}"
    
    prompts = [
        f"{date_range}の「経済・国際情勢」に関するニュースをDeep Researchで調査して詳細に報告して。",
        f"{date_range}の「最新AI・ITトレンド」をDeep Researchで調査して要約して。"
    ]

    for i, p in enumerate(prompts, 1):
        print(f"\n--- 質問{i}開始 ---")
        try:
            result = run_deep_research(p)
            send_line(f"【週刊リサーチ:{i}】\n\n{result}")
        except Exception as e:
            print(f"エラー発生: {e}")
            send_line(f"エラー発生: {e}")
