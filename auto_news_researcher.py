import os
from google import genai

def run_research():
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # 修正ポイント: 引数の名前を最新の仕様に合わせる
    interaction = client.interactions.create(
        model="gemini-2.0-flash-exp", # または使用可能な最新モデル
        input="2026年3月最終週の主要なテクノロジーニュースを5つ、背景を含めて要約してください。",
        config={
            "tools": [{"google_search_retrieval": {}}], # Deep Researchを有効化する設定
            "dynamic_retrieval_config": {
                "mode": "unspecified",
                "dynamic_threshold": 0.06
            }
        }
    )

    # 結果の取得（完了まで待機が必要な場合はポーリング処理を入れる）
    # ※ Interactions APIは非同期なため、statusを確認するループが必要です
    print(f"Research started! ID: {interaction.id}")
    
    # (簡易的な取得例。実際にはループでCOMPLETEDを待つ処理を推奨)
    result = client.interactions.get(interaction.id)
    # ... 以下、結果の保存処理など
