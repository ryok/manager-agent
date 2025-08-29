import os
from datetime import datetime, timedelta
from typing import Any, Optional

from notion_client import AsyncClient


class NotionClient:
    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")

        if not self.api_key:
            raise ValueError("Notion API key is required")

        self.client = AsyncClient(auth=self.api_key)

    async def get_weekly_updates(self, days: int = 7) -> dict[str, Any]:
        if not self.database_id:
            return {"items": [], "error": "Database ID not configured"}

        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()

            response = await self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Last edited time",
                    "date": {"after": start_date},
                },
                sorts=[{"property": "Last edited time", "direction": "descending"}],
            )

            items = self._parse_notion_results(response.get("results", []))
            return {"items": items, "count": len(items)}

        except Exception as e:
            return {"items": [], "error": str(e)}

    def _parse_notion_results(self, results: list[dict[str, Any]]) -> list[str]:
        parsed_items = []

        for page in results:
            try:
                properties = page.get("properties", {})

                title = self._extract_title(properties)
                status = self._extract_property(properties, "Status")
                priority = self._extract_property(properties, "Priority")

                if title:
                    item_text = title
                    if status:
                        item_text += f" (Status: {status})"
                    if priority:
                        item_text += f" [Priority: {priority}]"
                    parsed_items.append(item_text)

            except Exception as e:
                print(f"Error parsing Notion page: {e}")
                continue

        return parsed_items

    def _extract_title(self, properties: dict[str, Any]) -> str:
        for _prop_name, prop_value in properties.items():
            if prop_value.get("type") == "title":
                title_items = prop_value.get("title", [])
                if title_items and isinstance(title_items, list):
                    return title_items[0].get("text", {}).get("content", "")
        return ""

    def _extract_property(
        self, properties: dict[str, Any], property_name: str
    ) -> Optional[str]:
        prop = properties.get(property_name, {})
        prop_type = prop.get("type")

        if prop_type == "select":
            select_value = prop.get("select")
            if select_value:
                return select_value.get("name")
        elif prop_type == "status":
            status_value = prop.get("status")
            if status_value:
                return status_value.get("name")
        elif prop_type == "rich_text":
            text_items = prop.get("rich_text", [])
            if text_items and isinstance(text_items, list):
                return text_items[0].get("text", {}).get("content", "")

        return None

    async def create_page(self, title: str, content: str) -> dict[str, Any]:
        if not self.database_id:
            return {"success": False, "error": "Database ID not configured"}

        try:
            response = await self.client.pages.create(
                parent={"database_id": self.database_id},
                properties={"Name": {"title": [{"text": {"content": title}}]}},
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": content}}]
                        },
                    }
                ],
            )

            return {"success": True, "page_id": response["id"]}

        except Exception as e:
            return {"success": False, "error": str(e)}
