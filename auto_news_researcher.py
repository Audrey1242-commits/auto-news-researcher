import os  # 追加
import requests
from datetime import datetime, timedelta

# ===== 設定（環境変数から取得するように変更） =====
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
LINE_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("USER_ID")

# ===== 日付生成 =====
today = datetime.now()
past = today - timedelta(days=7)

date_to = today.strftime("%Y年%m月%d日")
date_from = past.strftime("%Y年%m月%d日")

date_range = f"{date_from}〜{date_to}"

# ===== Gemini呼び出し =====
def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    res = requests.post(url, json=body)
    data = res.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]

# ===== LINE送信 =====
def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message[:4900]  # LINE制限対策
            }
        ]
    }

    requests.post(url, headers=headers, json=body)

# ===== 質問テンプレ =====
prompts = [
# 質問1
f"""
過去7日間（{date_range}）の日本および世界の主要ニュースを信頼性の高い経済紙や公式発表を中心にリサーチし、
以下のカテゴリごとに重要なトピックを3つずつ抽出して要約してください。

カテゴリ：経済、国際情勢、政治

各トピックについて、「何が起きたか」だけでなく
「なぜ注目されているのか（背景や影響）」も含めて詳細なレポートを作成してください。
""",

# 質問2
f"""
過去7日間（{date_range}）の日本および世界の主要ニュースを信頼性の高い経済紙や公式発表を中心にリサーチし、
以下のカテゴリごとに重要なトピックを3つずつ抽出して要約してください。

カテゴリ：テクノロジー（AI含む）、ビジネストレンド、ITサービス

各トピックについて、「何が起きたか」と
「なぜ注目されているのか（背景や影響）」も含めて詳細なレポートを作成してください。
""",

# 質問3（拡張）
f"""
過去7日間（{date_range}）の日本および世界の主要ニュースを信頼性の高い経済紙や公式発表を中心にリサーチし、
以下のカテゴリごとに重要なトピックを3つずつ抽出して要約してください。

カテゴリ：テクノロジー（AI含む）、ビジネストレンド、ITサービス、企業リリース

各トピックについて、「何が起きたか」と
「なぜ注目されているのか（背景や影響）」も含めて詳細なレポートを作成してください。
""",

# 質問4
f"""
過去7日間（{date_range}）の日本および世界の主要ニュースを信頼性の高い経済紙や公式発表を中心にリサーチし、
以下のカテゴリごとに重要なトピックを3つずつ抽出して要約してください。

カテゴリ：エンタメ・カルチャー、科学（宇宙、物理、化学）、イベント／キャンペーン情報

各トピックについて、「何が起きたか」と
「なぜ注目されているのか（背景や影響）」も含めて詳細なレポートを作成してください。
""",

# 質問5（株）
f"""
過去7日間（{date_range}）の日本および世界の主要ニュースを信頼性の高い経済紙や公式発表を中心にリサーチし、
日本株、米国株における割安株をピックアップしてください。

なぜ割安になっているのか、
今後の期待値など含め詳細なレポートを作成してください。
"""
]

# ===== 実行 =====
for i, prompt in enumerate(prompts, 1):
    print(f"質問{i} 実行中...")

    try:
        result = ask_gemini(prompt)
    except Exception as e:
        result = "エラーが発生しました"

    message = f"【質問{i}の結果】\n{result}"

    send_line(message)
