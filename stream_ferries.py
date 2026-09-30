import asyncio
import json
import os
from datetime import datetime

import websockets
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("AISSTREAM_API_KEY")

STREAM_URL = "wss://stream.aisstream.io/v0/stream"

# East River, from the Battery up to about East 34th St
EAST_RIVER_BOX = [[40.698, -74.012], [40.750, -73.952]]


def fmt(value, unavailable, unit=""):
    """Return 'n/a' for AIS 'not available' codes, otherwise the value with a unit."""
    if value is None or value == unavailable:
        return "n/a"
    return f"{value}{unit}"


async def stream_positions():
    async with websockets.connect(STREAM_URL) as ws:
        subscription = {
            "APIKey": API_KEY,
            "BoundingBoxes": [EAST_RIVER_BOX],
            "FilterMessageTypes": ["PositionReport"],
        }
        await ws.send(json.dumps(subscription))

        async for raw in ws:
            msg = json.loads(raw)

            if "error" in msg:
                print("Server error:", msg["error"])
                return

            if msg.get("MessageType") == "SubscriptionConfirmation":
                print("Subscribed. Waiting for vessels...")
                continue

            if msg.get("MessageType") != "PositionReport":
                continue

            report = msg["Message"]["PositionReport"]

            if report["Latitude"] == 91 or report["Longitude"] == 181:
                continue

            name = msg.get("MetaData", {}).get("ShipName", "").strip() or "(unknown)"
            received = datetime.now().strftime("%H:%M:%S")

            print(
                f"{received}  {name:<20}  MMSI {report['UserID']}  "
                f"lat {report['Latitude']:.5f}  lon {report['Longitude']:.5f}  "
                f"speed {fmt(report['Sog'], 102.3, ' kn')}  "
                f"heading {fmt(report['TrueHeading'], 511, '°')}"
            )


if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit("No API key found - check your .env file")
    try:
        asyncio.run(stream_positions())
    except KeyboardInterrupt:
        print("\nStopped.")