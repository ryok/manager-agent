import re
from typing import Any


class DocumentParser:
    def __init__(self) -> None:
        self.patterns = {
            "achievements": [
                r"(?:成果|実績|完了|達成)[：:]\s*(.+)",
                r"(?:✓|✔|☑)\s*(.+)",
                r"(?:Done|DONE|done)[：:]\s*(.+)",
            ],
            "tasks": [
                r"(?:タスク|作業|進行中|TODO)[：:]\s*(.+)",
                r"(?:□|▢|☐)\s*(.+)",
                r"(?:In Progress|IN PROGRESS|WIP)[：:]\s*(.+)",
            ],
            "issues": [
                r"(?:課題|問題|懸念|リスク)[：:]\s*(.+)",
                r"(?:⚠|⚠️|❗|❌)\s*(.+)",
                r"(?:Issue|ISSUE|Problem|PROBLEM)[：:]\s*(.+)",
            ],
        }

    def parse(self, text: str) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {
            "achievements": [],
            "tasks": [],
            "issues": [],
            "raw_text": text,
        }

        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            for category, patterns in self.patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        content = match.group(1) if match.lastindex else match.group(0)
                        result[category].append(self._clean_text(content))
                        break

        if not any(result[cat] for cat in ["achievements", "tasks", "issues"]):
            result = self._fallback_parse(lines)

        return result

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"^\s*[-・●◆◇○]\s*", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _fallback_parse(self, lines: list[str]) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {
            "achievements": [],
            "tasks": [],
            "issues": [],
        }

        current_section = None
        section_keywords = {
            "achievements": ["成果", "実績", "完了", "achievement", "done"],
            "tasks": ["タスク", "作業", "予定", "task", "todo"],
            "issues": ["課題", "問題", "懸念", "issue", "problem"],
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            lower_line = line.lower()
            for section, keywords in section_keywords.items():
                if any(keyword in lower_line for keyword in keywords):
                    current_section = section
                    break

            if current_section and line.startswith(("-", "・", "●", "*", "+")):
                content = self._clean_text(line)
                if content:
                    result[current_section].append(content)

        return result

    def parse_markdown(self, markdown_text: str) -> dict[str, Any]:
        sections = {}
        current_heading = None
        current_content = []

        lines = markdown_text.split("\n")

        for line in lines:
            if line.startswith("#"):
                if current_heading:
                    sections[current_heading] = "\n".join(current_content).strip()

                heading_match = re.match(r"^#+\s*(.+)", line)
                if heading_match:
                    current_heading = heading_match.group(1).strip()
                    current_content = []
            else:
                current_content.append(line)

        if current_heading:
            sections[current_heading] = "\n".join(current_content).strip()

        return sections
