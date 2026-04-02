import os
import time
import requests
from datetime import datetime, timedelta

# ===== 1. 設定（GitHub Secretsから読み込み） =====
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
LINE_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("USER_ID")

# ===== 2. 日付生成 =====
today = datetime.now()
past = today - timedelta(days=7)
date_range = f"{past.strftime('%Y年%m月%d日')}〜{today.strftime('%Y年%m月%d日')}"

# ===== 3. Deep Research実行関数 (HTTP直接リクエスト版) =====
def run_deep_research(prompt):
    # APIエンドポイント (v1betaを使用)
    # モデルは Deep Research に対応した gemini-2.0-flash を指定
    create_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:createInteraction?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    # SDKが自動生成するはずのJSON構造を「手書き」で定義
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

    # リサーチ開始のPOSTリクエスト
    response = requests.post(create_url, headers=headers, json=body)
    res_data = response.json()

    if "error" in res_data:
        raise Exception(f"APIリクエストエラー: {res_data['error']['message']}")

    # interactionのIDを取得 (形式: names/interactions/XXX -> XXXを取り出す)
    resource_name = res_data.get("name", "")
    interaction_id = resource_name.split("/")[-1]
    
    print(f"リサーチ開始成功 (ID: {interaction_id})")

    # ステータス確認用のURL
    status_url = f"https://generativelanguage.googleapis.com/v1beta/interactions/{interaction_id}?key={GEMINI_API_KEY}"
    
    # 完了までポーリング（ループ）
    while True:
        status_res = requests.get(status_url)
        status_data = status_res.json()
        
        state = status_data.get("state", "UNKNOWN")
        
        if state == "COMPLETED":
            print("リサーチ完了！結果を取得します。")
            # 結果のテキストを抽出
            return status_data["result"]["text"]
        
        elif state == "FAILED":
            error_info = status_data.get("error", "不明なエラー")
            raise Exception(f"Deep Researchが失敗しました: {error_info}")
        
        print(f"調査中... (現在のステータス: {state})")
        # Deep Researchは時間がかかるため、間隔を長め（30秒）に設定
        time.sleep(30)

# ===== 4. LINE送信関数 =====
def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    # LINEの1メッセージ制限（5000文字）に配慮
    body = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message[:4900]
            }
        ]
    }
    res = requests.post(url, headers=headers, json=body)
    if res.status_code != 200:
        print(f"LINE送信失敗: {res.text}")

# ===== 5. メイン処理 =====
if __name__ == "__main__":
    prompts = [
        f"{date_range}の日本および世界の「経済・国際情勢・政治」に関する主要ニュースをリサーチし、詳細レポートを作成して。",
        f"{date_range}の「AI・半導体・ITサービス」に関する最新ニュースとビジネストレンドをリサーチして。",
        f"{date_range}の日本株・米国株における、現在の市場環境で注目すべき銘柄とその理由をリサーチして。"
    ]

    for i, p in enumerate(prompts, 1):
        print(f"\n--- 質問{i}を実行中 ---")
        try:
            # Deep Researchの実行
            result_text = run_deep_research(p)
            
            # 結果をLINEで送信
            send_line(f"【質問{i}：Deep Research結果】\n\n{result_text}")
            print(f"質問{i} の結果をLINEに送信しました。")
            
        except Exception as e:
            error_msg = f"質問{i} の実行中にエラーが発生しました:\n{str(e)}"
            print(error_msg)
            send_line(error_msg)
        
        # 連続実行による負荷軽減のため、少し待機
        time.sleep(5)
