from typing import Any

from agents.base_agent import BaseAgent
from config.agent_config import MANAGER_CONFIG


class ManagerAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(MANAGER_CONFIG)

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        final_report = input_data.get("final_report", "")
        review_feedback = input_data.get("review_feedback", {})

        if not final_report:
            return {
                "status": "error",
                "message": "最終版の週報が提供されていません",
            }

        manager_comment = await self._generate_manager_comment(
            final_report, review_feedback
        )

        return {
            "status": "success",
            "comment": manager_comment["comment"],
            "evaluation": manager_comment["evaluation"],
            "next_week_expectations": manager_comment["expectations"],
            "metadata": {
                "agent": self.config.name,
                "approval_status": manager_comment["approval"],
            },
        }

    async def _generate_manager_comment(
        self, report: str, review_feedback: dict[str, Any]
    ) -> dict[str, Any]:
        review_score = review_feedback.get("score", "不明")

        prompt = f"""
あなたは部下の週報を確認する上司として、以下の週報に対してコメントを提供してください。

## 週報内容
{report}

## レビュー結果
スコア: {review_score}/10

## コメント作成のガイドライン
1. 成果を適切に評価し、具体的に褒める
2. 改善が必要な点があれば建設的にフィードバック
3. 次週への期待とアドバイスを含める
4. モチベーションを高める励ましの言葉を添える

## 出力形式
以下の形式でコメントを提供してください：

### 総評
[全体的な評価とコメント]

### 特に評価する点
- [評価点1]
- [評価点2]

### 改善提案・アドバイス
- [提案1]
- [提案2]

### 来週への期待
[次週に期待することや応援メッセージ]

### 承認ステータス
[承認/要確認]
"""

        response = await self.generate_response(prompt)

        return self._parse_manager_response(response)

    def _parse_manager_response(self, response: str) -> dict[str, Any]:
        lines = response.split("\n")

        comment = ""
        evaluation = []
        expectations = ""
        approval = "承認"

        current_section = None

        for line in lines:
            line = line.strip()

            if "総評" in line:
                current_section = "comment"
            elif "特に評価する点" in line:
                current_section = "evaluation"
            elif "改善提案" in line or "アドバイス" in line:
                current_section = "advice"
            elif "来週への期待" in line:
                current_section = "expectations"
            elif "承認ステータス" in line:
                current_section = "approval"
            elif line:
                if current_section == "comment":
                    comment += line + "\n"
                elif current_section == "evaluation" and line.startswith("-"):
                    evaluation.append(line[1:].strip())
                elif current_section == "expectations":
                    expectations += line + "\n"
                elif current_section == "approval" and ("承認" in line or "要確認" in line):
                    approval = line

        return {
            "comment": comment.strip(),
            "evaluation": evaluation,
            "expectations": expectations.strip(),
            "approval": approval,
        }
