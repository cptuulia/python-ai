
################################################################
#
# Example of using tools (function calling).
# We get the current weather for a location by calling a public API from the model.
#
#################################################################
import requests
import json
import config



from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.BASE_URL)
"""
docs: https://platform.openai.com/docs/guides/function-calling
"""

# --------------------------------------------------------------
# Define the tool (function) that we want to call
# --------------------------------------------------------------


def get_weather(latitude, longitude):
    """This is a publically available API that returns the weather for a given location."""
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]


# --------------------------------------------------------------
# Step 1: Call model with get_weather tool defined
# --------------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for provided coordinates in celsius.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

system_prompt = "You are a helpful weather assistant."

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What's the weather like in Paris today?"},
]

completion = client.chat.completions.create(
    model=config.OPENAI_MODEL,
    messages=messages,
    tools=tools,
)

# --------------------------------------------------------------
# Step 2: Model decides to call function(s)
# --------------------------------------------------------------

completion.model_dump()

# --------------------------------------------------------------
# Step 3: Execute get_weather function
# --------------------------------------------------------------


def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)
    # **args unpacks this dictionary, so the function call becomes 
    # get_weather(latitude=48.8566, longitude=2.3522) instead of 
    # get_weather({"latitude": 48.8566, "longitude": 2.3522}).

messages.append(completion.choices[0].message)
for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    

    result = call_function(name, args)
    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
    )


    #
    # json.loads() converts a JSON-formatted string into a corresponding Python object.
    #
    # json.dumps() converts a Python object (such as a dictionary or list) 
    # into a JSON-formatted string

# --------------------------------------------------------------
# Step 4: Supply result and call model again
# --------------------------------------------------------------


class WeatherResponse(BaseModel):
    temperature: float = Field(
        description="The current temperature in celsius for the given location."
    )
    response: str = Field(
        description="A natural language response to the user's question."
    )

    
# completion_2 = client.beta.chat.completions.parse(
#    model=config.OPENAI_MODEL,
#    messages=messages,
#    tools=tools,
#    response_format=WeatherResponse,
#)
completion_2 = client.chat.completions.create(
    model=config.OPENAI_MODEL,
    messages=messages,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "calendar_event",
            "schema": WeatherResponse.model_json_schema(),
        },
    },
)
# --------------------------------------------------------------
# Step 5: Check model response
# --------------------------------------------------------------

#final_response = completion_2.choices[0].message.parsed
final_response = WeatherResponse.model_validate_json(completion_2.choices[0].message.content)
final_response.temperature
final_response.response
print(final_response.response)
