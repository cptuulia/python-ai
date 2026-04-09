import requests
import json
import config


import os
from openai import OpenAI
from pydantic import BaseModel, Field



def get_weather(latitude, longitude, name):
    """This is a publically available API that returns the weather for a given location."""
    #https://api.open-meteo.com/v1/forecast?latitude=&longitude=13.41&current=cloud_cover
     # f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = requests.get(
          f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=cloud_cover"  
    )
    data = response.json()
    retval =  data["current"]
    retval['name'] = name
   
    return retval


#x= get_weather(62.000, 24.4200, 'espoo' )

client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.BASE_URL)

system_prompt = "You are a helpful weather assistant."

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current could cover for provided coordinates in percentage.",
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
    {"role": "user", "content": "Tell me weather in the cities in Amsterdam, Haarlem and Alkmaar"},
]

completion = client.chat.completions.create(
    model=config.OPENAI_MODEL,
    messages=messages,
    tools=tools
)
completion.model_dump()
#print(completion.choices[0].message)


def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)
    

if completion.choices[0].message.tool_calls:
    for tool_call in completion.choices[0].message.tool_calls: 
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        messages.append(completion.choices[0].message)

        result = call_function(name, args)
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
        )
else:
    print("No tool calls were made by the model. Response:", completion.choices[0].message.content)

#json_formatted_str = json.dumps(messages, indent=2)
#print(json_formatted_str)


class WeatherResponse(BaseModel):
    
    cloud_cover: str = Field(
        description="The current cloud cover in percentage for the given location."
    )
    name: str = Field(
        description="Name for the given location."
    )
    response: str = Field(
        description="A natural language response to the user's question."
    )


completion_2 = client.chat.completions.create(
    model=config.OPENAI_MODEL,
    messages=messages,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "calendar_event",
            "schema": WeatherResponse.schema(),
        },
    },
)

final_response =WeatherResponse.parse_raw(completion_2.choices[0].message.content)
final_response.temperature
final_response.response
print(final_response.response)