from openai import OpenAI
from .openai_client import OpenAIClient

from .weather_service import WeatherService


def main() -> None:
   
    client = OpenAIClient()
    service = WeatherService(client)

    user_message = (
        "Tell me all of the cities where the weather is sunny on the following list: "
        "Madrid, Berlin, Rome, Espoo, Paris, London or Amsterdam. "
        "It is sunny when cloud cover is less than 50%."
    )

    result = service.find_sunny_cities(user_message)
    print(result)


if __name__ == "__main__":
    main()
