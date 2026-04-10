import config
from openai import OpenAI
from typing import Any, Optional


class OpenAIClient:
    """Light wrapper around the OpenAI client to centralize configuration.

    Keeps a simple API so the rest of the code can be tested/mocked easily.
    """

    def __init__(
            self, 
            api_key: Optional[str] = None, 
            base_url: Optional[str] = None, 
            model: Optional[str] = None):
            self.client = OpenAI(   api_key=api_key or config.OPENAI_API_KEY, 
                                    base_url=base_url or config.BASE_URL
            )
            self.model = model or config.OPENAI_MODEL

    def create_completion(self, messages: list[dict], tools: Optional[list] = None, response_format: Optional[dict] = None) -> Any:
        kwargs: dict = {"model": self.model, "messages": messages}
        if tools is not None:
            kwargs["tools"] = tools
        if response_format is not None:
            kwargs["response_format"] = response_format
        return self.client.chat.completions.create(**kwargs)
