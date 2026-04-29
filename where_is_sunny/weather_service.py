import json
import requests
from typing import Optional

from .models import WeatherResponse
#from .openai_client import OpenAIClient
from lib.openai_client import OpenAIClient

class WeatherService:
    """Service responsible for interacting with the weather API and model."""

    def __init__(self, client: OpenAIClient):
        self.client = client

    def get_weather(self, latitude: float, longitude: float, name: str) -> dict:
        resp = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=cloud_cover&current=temperature_2m"
        )
        data = resp.json()
        retval = data.get("current", {})    
        retval["name"] = name
        return retval

    def find_sunny_cities(self, user_message: str) -> WeatherResponse:
        system_prompt = "You are a helpful weather assistant."

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current cloud cover for provided coordinates in percentage.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                            "name": {"type": "string"},
                        },
                        "required": ["latitude", "longitude", "name"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            }
        ]

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        # First pass: ask model which tools to call
        completion = self.client.create_completion(messages=messages, tools=tools)
        messages.append(completion.choices[0].message)

        # If model requested tool calls, execute them and append tool outputs
        if completion.choices[0].message.tool_calls:
            for tool_call in completion.choices[0].message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = self.get_weather(**args)
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})

        # Second pass: ask model to return structured JSON with the sunny cities
        completion_2 = self.client.create_completion(
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "calendar_event", "schema": WeatherResponse.schema()},
            },
        )

        final = WeatherResponse.parse_raw(completion_2.choices[0].message.content)
        return final
