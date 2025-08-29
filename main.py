import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv

from agents.manager import ManagerAgent
from agents.report_writer import ReportWriterAgent
from agents.reviewer import ReviewerAgent
from tools.notion_tools import NotionClient


class WeeklyReportSystem:
    def __init__(self, mode: str = "development") -> None:
        self.mode = mode
        self._load_environment()
        self._initialize_agents()

    def _load_environment(self) -> None:
        load_dotenv()

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables")

        genai.configure(api_key=api_key)

    def _initialize_agents(self) -> None:
        self.report_writer = ReportWriterAgent()
        self.reviewer = ReviewerAgent()
        self.manager = ManagerAgent()

        notion_api_key = os.getenv("NOTION_API_KEY")
        notion_db_id = os.getenv("NOTION_DATABASE_ID")

        if notion_api_key and notion_db_id:
            notion_client = NotionClient(notion_api_key, notion_db_id)
            self.report_writer.set_notion_client(notion_client)
            print("✓ Notion integration enabled")
        else:
            print("⚠ Notion integration disabled (missing API key or database ID)")

    async def process_weekly_report(
        self, meeting_notes: list[str], use_notion: bool = True
    ) -> dict[str, Any]:
        print("\n" + "=" * 60)
        print("週報作成システム - 処理開始")
        print("=" * 60)

        print("\n[1/4] 週報ドラフト作成中...")
        draft_result = await self.report_writer.process(
            {
                "meeting_notes": meeting_notes,
                "notion_updates": {"enabled": use_notion},
            }
        )

        if draft_result["status"] != "success":
            return {"error": "Failed to create draft", "details": draft_result}

        draft = draft_result["draft"]
        print("✓ ドラフト作成完了")

        print("\n[2/4] レビュー実施中...")
        review_result = await self.reviewer.process({"draft": draft})

        if review_result["status"] != "success":
            return {"error": "Failed to review draft", "details": review_result}

        print(f"✓ レビュー完了 (スコア: {review_result['metadata']['review_score']}/10)")

        print("\n[3/4] フィードバック反映中...")
        if review_result["suggestions"]:
            improvement_prompt = self._create_improvement_prompt(
                draft, review_result["suggestions"]
            )
            improved_draft = await self.report_writer.generate_response(
                improvement_prompt
            )
        else:
            improved_draft = draft

        print("✓ 改善版作成完了")

        print("\n[4/4] 上司コメント生成中...")
        manager_result = await self.manager.process(
            {
                "final_report": improved_draft,
                "review_feedback": {"score": review_result["metadata"]["review_score"]},
            }
        )

        if manager_result["status"] != "success":
            return {"error": "Failed to get manager comment", "details": manager_result}

        print("✓ 上司コメント生成完了")

        return {
            "status": "success",
            "final_report": improved_draft,
            "review_feedback": review_result,
            "manager_comment": manager_result,
            "timestamp": datetime.now().isoformat(),
        }

    def _create_improvement_prompt(
        self, draft: str, suggestions: list[str]
    ) -> str:
        suggestions_text = "\n".join(f"- {s}" for s in suggestions)
        return f"""
以下の週報ドラフトを、レビューフィードバックに基づいて改善してください。

## 元のドラフト
{draft}

## 改善提案
{suggestions_text}

改善版の週報を作成してください。形式は元のドラフトと同じにしてください。
"""

    def save_report(self, result: dict[str, Any], output_dir: str = "output") -> str:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_path / f"weekly_report_{timestamp}.md"

        content = self._format_final_output(result)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        return str(filename)

    def _format_final_output(self, result: dict[str, Any]) -> str:
        output = f"""# 週報 - {datetime.now().strftime('%Y年%m月%d日')}

## 週報内容
{result['final_report']}

---

## レビュー結果
**スコア**: {result['review_feedback']['metadata']['review_score']}/10

### フィードバック
{result['review_feedback']['review']}

### 改善提案
"""
        for suggestion in result["review_feedback"]["suggestions"]:
            output += f"- {suggestion}\n"

        output += f"""
---

## 上司コメント
### 総評
{result['manager_comment']['comment']}

### 特に評価する点
"""
        for point in result["manager_comment"]["evaluation"]:
            output += f"- {point}\n"

        output += f"""
### 来週への期待
{result['manager_comment']['next_week_expectations']}

**承認ステータス**: {result['manager_comment']['metadata']['approval_status']}
"""

        return output


def load_meeting_notes(file_paths: list[str]) -> list[str]:
    notes = []
    for path in file_paths:
        if Path(path).exists():
            with open(path, encoding="utf-8") as f:
                notes.append(f.read())
            print(f"✓ 議事録読み込み: {path}")
        else:
            print(f"⚠ ファイルが見つかりません: {path}")
    return notes


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="週報作成マルチエージェントシステム"
    )
    parser.add_argument(
        "--mode",
        choices=["development", "production"],
        default="development",
        help="実行モード",
    )
    parser.add_argument(
        "--notes",
        nargs="*",
        help="議事録ファイルのパス（複数指定可）",
    )
    parser.add_argument(
        "--no-notion",
        action="store_true",
        help="Notion連携を無効化",
    )
    parser.add_argument(
        "--output",
        default="output",
        help="出力ディレクトリ",
    )

    args = parser.parse_args()

    system = WeeklyReportSystem(mode=args.mode)

    meeting_notes = []
    if args.notes:
        meeting_notes = load_meeting_notes(args.notes)
    else:
        print("議事録ファイルが指定されていません。サンプルデータを使用します。")
        meeting_notes = [
            """
            ## 2024年12月20日 定例会議

            ### 議題
            - プロジェクトA進捗確認
            - 来週のリリース準備

            ### 決定事項
            ✓ プロジェクトAのフェーズ1完了
            ✓ リリース日を12月25日に決定

            ### タスク
            □ ドキュメント更新（担当：田中）
            □ テスト環境の準備（担当：佐藤）

            ### 課題
            ⚠ パフォーマンステストで目標値未達
            ⚠ リソース不足の懸念あり
            """
        ]

    result = await system.process_weekly_report(
        meeting_notes, use_notion=not args.no_notion
    )

    if result.get("status") == "success":
        output_file = system.save_report(result, args.output)
        print(f"\n✓ 週報を保存しました: {output_file}")
    else:
        print(f"\n✗ エラーが発生しました: {result}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
