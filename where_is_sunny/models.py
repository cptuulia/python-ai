from pydantic import BaseModel, Field
from typing import List


class WeatherResponse(BaseModel):
    """Structured response listing cities where it is sunny."""
    cities: List[str] = Field(description="The cities where the weather is sunny.")
