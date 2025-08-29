from datetime import datetime
from typing import Any, Optional

from agents.base_agent import BaseAgent
from config.agent_config import REPORT_WRITER_CONFIG
from tools.document_parser import DocumentParser
from tools.notion_tools import NotionClient


class ReportWriterAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(REPORT_WRITER_CONFIG)
        self.document_parser = DocumentParser()
        self.notion_client: Optional[NotionClient] = None

    def set_notion_client(self, notion_client: NotionClient) -> None:
        self.notion_client = notion_client

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        meeting_notes = input_data.get("meeting_notes", [])
        notion_updates = input_data.get("notion_updates", {})

        parsed_notes = self._parse_meeting_notes(meeting_notes)

        notion_data = {}
        if self.notion_client and notion_updates.get("enabled"):
            notion_data = await self._fetch_notion_updates()

        report_draft = await self._generate_report(parsed_notes, notion_data)

        return {
            "status": "success",
            "draft": report_draft,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "agent": self.config.name,
                "sources": {
                    "meeting_notes_count": len(meeting_notes),
                    "notion_items_count": len(notion_data.get("items", [])),
                },
            },
        }

    def _parse_meeting_notes(self, notes: list[str]) -> dict[str, Any]:
        parsed_data = {"achievements": [], "tasks": [], "issues": []}

        for note in notes:
            parsed = self.document_parser.parse(note)
            parsed_data["achievements"].extend(parsed.get("achievements", []))
            parsed_data["tasks"].extend(parsed.get("tasks", []))
            parsed_data["issues"].extend(parsed.get("issues", []))

        return parsed_data

    async def _fetch_notion_updates(self) -> dict[str, Any]:
        if not self.notion_client:
            return {}

        try:
            updates = await self.notion_client.get_weekly_updates()
            return updates
        except Exception as e:
            print(f"Error fetching Notion updates: {e}")
            return {}

    async def _generate_report(
        self, parsed_notes: dict[str, Any], notion_data: dict[str, Any]
    ) -> str:
        prompt = self._create_report_prompt(parsed_notes, notion_data)
        report = await self.generate_response(prompt)
        return report

    def _create_report_prompt(
        self, parsed_notes: dict[str, Any], notion_data: dict[str, Any]
    ) -> str:
        current_date = datetime.now().strftime("%Y年%m月%d日")

        achievements = "\n".join(
            f"- {item}" for item in parsed_notes.get("achievements", [])
        )
        tasks = "\n".join(f"- {item}" for item in parsed_notes.get("tasks", []))
        issues = "\n".join(f"- {item}" for item in parsed_notes.get("issues", []))

        notion_items = ""
        if notion_data.get("items"):
            notion_items = "\n\nNotion更新情報:\n" + "\n".join(
                f"- {item}" for item in notion_data.get("items", [])
            )

        prompt = f"""
以下の情報を基に、{current_date}の週報を作成してください。

## 収集した情報

### 成果・実績
{achievements or "- なし"}

### タスク状況
{tasks or "- なし"}

### 課題・懸念事項
{issues or "- なし"}
{notion_items}

## 作成する週報の形式
標準の週報テンプレートに従って、簡潔かつ分かりやすくまとめてください。
各セクションには具体的な内容を記載し、進捗率や期限などの数値情報があれば含めてください。
"""
        return prompt
