################################################################
#
# Example to get the current weather for a list of cities 
# and return the ones where it's sunny.
#
#################################################################
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
    {"role": "user", "content": "Tell me  all of the cities where the weather is sunny on the following list  : Madrid, Berlin, Rome,  Espoo, Paris,  London or Amsterdam. "},
]
#  {"role": "user", "content": "Tell mein which of following the cities in Amsterdam, Haarlem and Alkmaar"},
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
    
messages.append(completion.choices[0].message)
if completion.choices[0].message.tool_calls:
    for tool_call in completion.choices[0].message.tool_calls: 
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
       

        result = call_function(name, args)
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
        )
else:
    print("No tool calls were made by the model. Response:", completion.choices[0].message.content)

#json_formatted_str = json.dumps(messages, indent=2)
#print(json_formatted_str)


class WeatherResponse(BaseModel):
    cities: list[str] = Field(
        description="The cities where the weather is sunny."
    )


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

final_response =WeatherResponse.model_validate_json(completion_2.choices[0].message.content)
print(final_response)