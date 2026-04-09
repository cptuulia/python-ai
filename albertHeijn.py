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
    return data["current"]


#x= get_weather(62.000, 24.4200, 'espoo )

client = OpenAI(api_key=config.OPENAI_API_KEY)

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
    {"role": "user", "content": "Tell me the cities in Noord Holland (Amsterdam, Haarlem, Alkmaar, Den Helder, Zaandam (Zaanstad), Hoorn, Purmerend, Beverwijk, Heerhugowaard, Castricum, Bergen, Schagen ) where the weather is sunny today."},
]

completion = client.chat.completions.create(
    model=config.OPENAI_MODEL,
    messages=messages,
    tools=tools
    
)
completion.model_dump()
print(completion.choices[0].message)


