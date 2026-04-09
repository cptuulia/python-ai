################################################################
#
# Basic example

#################################################################

import config

from openai import OpenAI
 

client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.BASE_URL)


completion = client.chat.completions.create(
    model=config.OPENAI_MODEL,
    messages=[
        {"role": "system", "content": "You're a helpful assistant."},
        {
            "role": "user",
            "content": "Write a limerick about the Python programming language.",
        },
    ],
)

response = completion.choices[0].message.content
print(response)