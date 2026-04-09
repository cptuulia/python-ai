################################################################
#
# Example of using structured output with Pydantic models.

#################################################################

import os
import config

from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.BASE_URL)


# --------------------------------------------------------------
# Step 1: Define the response format in a Pydantic model
# --------------------------------------------------------------

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


# --------------------------------------------------------------
# Step 2: Call the model
# --------------------------------------------------------------

completion = client.chat.completions.create(
    model=config.OPENAI_MODEL,
    messages=[
        {"role": "system", "content": "Extract the event information."},
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday.",
        },
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "calendar_evesnt",
            "schema": CalendarEvent.schema(),
        },
    },
)

# --------------------------------------------------------------
# Step 3: Parse the response
# --------------------------------------------------------------

event = CalendarEvent.parse_raw(completion.choices[0].message.content)
print(event.name)
print(event.date)
print(event.participants)