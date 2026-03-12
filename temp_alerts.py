import logging
import os
from datetime import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests
import azure.functions as func

app = func.FunctionApp()

# Coordinates for zip code 27519 (Cary, NC)
LAT = 35.7915
LON = -78.8107

# WhatsApp via CallMeBot (free, no limits)
PHONE_NUMBER = "19195929646"  # international format, no +
CALLMEBOT_API_KEY = os.environ.get("CALLMEBOT_API_KEY", "8233014")


def fetch_temperature() -> float:
    """Fetch current temperature in Fahrenheit for the configured location."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m"
        f"&temperature_unit=fahrenheit"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()["current"]["temperature_2m"]


def send_whatsapp(message: str) -> None:
    """Send WhatsApp message via CallMeBot."""
    url = (
        f"https://api.callmebot.com/whatsapp.php"
        f"?phone={PHONE_NUMBER}"
        f"&text={quote(message)}"
        f"&apikey={CALLMEBOT_API_KEY}"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    if "Message queued" not in resp.text and "OK" not in resp.text:
        raise RuntimeError(f"CallMeBot error: {resp.text}")


@app.function_name(name="WeatherWhatsApp")
@app.route(route="weather-whatsapp", methods=["GET", "POST"], auth_level=func.AuthLevel.ANONYMOUS)
def weather_whatsapp(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("WeatherWhatsApp function triggered.")

    try:
        temp_f = fetch_temperature()
    except Exception as e:
        logging.error(f"Failed to fetch weather: {e}")
        return func.HttpResponse(f"Error fetching weather data: {e}", status_code=500)

    now = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %I:%M:%S %p %Z")
    message = f"Cary, NC (27519): {temp_f}\u00b0F\n{now}"
    logging.info(f"Weather fetched: {message}")

    try:
        send_whatsapp(message)
    except Exception as e:
        logging.error(f"Failed to send WhatsApp: {e}")
        return func.HttpResponse(
            f"Temperature fetched ({temp_f}\u00b0F) but WhatsApp failed: {e}",
            status_code=500,
        )

    logging.info(f"WhatsApp sent to {PHONE_NUMBER}")
    return func.HttpResponse(
        f"Success! Temp: {temp_f}\u00b0F. WhatsApp sent to {PHONE_NUMBER}.",
        status_code=200,
    )
