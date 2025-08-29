from typing import Any

from agents.base_agent import BaseAgent
from config.agent_config import REVIEWER_CONFIG


class ReviewerAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(REVIEWER_CONFIG)

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        draft = input_data.get("draft", "")

        if not draft:
            return {
                "status": "error",
                "message": "週報ドラフトが提供されていません",
            }

        review_result = await self._review_draft(draft)

        return {
            "status": "success",
            "review": review_result["feedback"],
            "suggestions": review_result["suggestions"],
            "approval": review_result["approval"],
            "metadata": {
                "agent": self.config.name,
                "review_score": review_result.get("score", 0),
            },
        }

    async def _review_draft(self, draft: str) -> dict[str, Any]:
        prompt = f"""
以下の週報ドラフトをレビューしてください。

## 週報ドラフト
{draft}

## レビュー観点
1. 内容の完全性（必要な情報が含まれているか）
2. 文章の明確性（誤解を招かない表現か）
3. 構成の論理性（情報が適切に整理されているか）
4. 具体性（数値や期限が明記されているか）

## 出力形式
以下の形式でレビュー結果を提供してください：

### フィードバック
[全体的な評価と主要な改善点]

### 具体的な改善提案
1. [改善提案1]
2. [改善提案2]
...

### 承認ステータス
[承認/条件付き承認/要修正]

### スコア
[10点満点での評価]
"""

        response = await self.generate_response(prompt)

        return self._parse_review_response(response)

    def _parse_review_response(self, response: str) -> dict[str, Any]:
        lines = response.split("\n")

        feedback = ""
        suggestions = []
        approval = "要修正"
        score = 0

        current_section = None

        for line in lines:
            line = line.strip()

            if "フィードバック" in line:
                current_section = "feedback"
            elif "具体的な改善提案" in line:
                current_section = "suggestions"
            elif "承認ステータス" in line:
                current_section = "approval"
            elif "スコア" in line:
                current_section = "score"
            elif line:
                if current_section == "feedback":
                    feedback += line + "\n"
                elif current_section == "suggestions" and line.startswith(
                    tuple("123456789")
                ):
                    suggestions.append(line)
                elif current_section == "approval":
                    if "承認" in line:
                        approval = line
                elif current_section == "score":
                    try:
                        score = int("".join(filter(str.isdigit, line)))
                    except ValueError:
                        score = 0

        return {
            "feedback": feedback.strip(),
            "suggestions": suggestions,
            "approval": approval,
            "score": score,
        }
