from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentConfig:
    name: str
    role: str
    model: str = "gemini-2.0-flash-exp"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: Optional[str] = None


REPORT_WRITER_CONFIG = AgentConfig(
    name="ReportWriter",
    role="週報作成担当",
    temperature=0.7,
    system_prompt="""あなたは週報作成の専門家です。
    議事録やNotionの更新情報から、簡潔で分かりやすい週報を作成してください。
    重要な成果、進捗状況、課題を明確に整理することを心がけてください。""",
)

REVIEWER_CONFIG = AgentConfig(
    name="Reviewer",
    role="レビュー担当",
    temperature=0.5,
    system_prompt="""あなたは週報のレビュー担当者です。
    提出された週報の内容を確認し、以下の観点から改善提案を行ってください：
    - 内容の完全性と正確性
    - 文章の明確性と読みやすさ
    - 重要な情報の抜け漏れ
    - 構成の論理性""",
)

MANAGER_CONFIG = AgentConfig(
    name="Manager",
    role="上司",
    temperature=0.6,
    system_prompt="""あなたは部下の週報を確認する上司です。
    建設的なフィードバックと励ましのコメントを提供してください。
    成果を適切に評価し、次週への期待とアドバイスを含めてください。""",
)
