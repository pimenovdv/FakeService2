from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/api/weather",
    tags=["weather"]
)

class WeatherResponse(BaseModel):
    city: str
    temperature: float
    condition: str
    humidity: int
    wind_speed: float

@router.get("", response_model=WeatherResponse)
async def get_weather(city: str = Query(..., description="The city to get weather for")):
    # Mock some data based on the city
    if city.lower() == "london":
        return WeatherResponse(
            city="London",
            temperature=15.0,
            condition="Rainy",
            humidity=80,
            wind_speed=12.5
        )
    elif city.lower() == "tokyo":
        return WeatherResponse(
            city="Tokyo",
            temperature=22.5,
            condition="Sunny",
            humidity=50,
            wind_speed=8.0
        )
    elif city.lower() == "new york":
        return WeatherResponse(
            city="New York",
            temperature=18.0,
            condition="Cloudy",
            humidity=60,
            wind_speed=15.2
        )
    else:
        # Default mock response for any other city
        return WeatherResponse(
            city=city.title(),
            temperature=20.0,
            condition="Partly Cloudy",
            humidity=55,
            wind_speed=10.0
        )
