from abc import ABC, abstractmethod
from typing import Any

import google.generativeai as genai

from config.agent_config import AgentConfig


class BaseAgent(ABC):
    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.model = genai.GenerativeModel(
            model_name=config.model,
            generation_config={
                "temperature": config.temperature,
                "max_output_tokens": config.max_tokens,
            },
        )
        self.conversation_history: list[dict[str, Any]] = []

    @abstractmethod
    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        pass

    def generate_prompt(self, template: str, **kwargs: Any) -> str:
        return template.format(**kwargs)

    async def generate_response(self, prompt: str) -> str:
        if self.config.system_prompt:
            full_prompt = f"{self.config.system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        response = self.model.generate_content(full_prompt)
        return response.text

    def add_to_history(self, role: str, content: str) -> None:
        self.conversation_history.append({"role": role, "content": content})

    def get_history(self) -> list[dict[str, Any]]:
        return self.conversation_history

    def clear_history(self) -> None:
        self.conversation_history = []
