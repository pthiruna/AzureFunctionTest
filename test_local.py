"""
Local test script — calls the functions in temp_alerts.py directly.
Usage: python3 test_local.py
"""

from temp_alerts import fetch_temperature, send_whatsapp


def main():
    print("Fetching temperature...")
    temp_f = fetch_temperature()
    message = f"Cary, NC (27519): {temp_f}\u00b0F"
    print(f"  {message}")

    print("Sending WhatsApp...")
    send_whatsapp(message)
    print("  WhatsApp sent successfully!")


if __name__ == "__main__":
    main()
