import os
from google import genai

def run_research():
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # リサーチ実行
    prompt = "2026年3月最終週の主要なテクノロジーニュースを5つ、背景を含めて要約してください。"
    interaction = client.interactions.create(
        model="gemini-3-flash",
        tool="deep_research",
        prompt=prompt
    )

    # 完了まで待機して結果を取得
    # (Actionsのタイムアウト設定内で終わるよう調整)
    result = interaction.result.text
    
    # 結果を一時ファイルに書き出す（次のステップでIssueに投稿するため）
    with open("result.md", "w", encoding="utf-8") as f:
        f.write(f"# 今週のDeep Research報告\n\n{result}")

if __name__ == "__main__":
    run_research()