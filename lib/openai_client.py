##########################################################
#
# This module defines the OpenAIClient class,
# which serves as a wrapper around the OpenAI API client. 
# It provides a method to create chat completions using 
# the specified model, messages, tools, and response format. 
# 
#
###########################################################

import config
from openai import OpenAI
from typing import Any, Optional


class OpenAIClient:

    def __init__(self) -> None:
        self.client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.BASE_URL)
        self.model = config.OPENAI_MODEL

    def create_completion(
              self, 
              messages: list[dict], 
              tools: Optional[list] = None, 
              response_format: Optional[dict] = None
        ) -> Any:
        args: dict = {"model": self.model, "messages": messages}
        if tools is not None:
            args["tools"] = tools
        if response_format is not None:
            args["response_format"] = response_format
        return self.client.chat.completions.create(**args)