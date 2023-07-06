"""
Dummy Heart Rate Client Script.

This script connects to a Frisbee Server using WebSockets and performs authentication.
It authenticates with the server, receives messages from the server, and optionally sends heart rate data to ThingSpeak.

The script uses the aiohttp and websockets libraries for WebSocket communication and the numpy and matplotlib libraries for
generating and plotting heart rate data.

"""


import asyncio
import json
import sys

import aiohttp
import websockets

import numpy as np
import matplotlib.pyplot as plt


URL = 'ws://127.0.0.1:8001'
# URL = 'ws://127.0.0.1:8080/ws'
ADMIN_PASSWORD = 'admin'
SEND_DATA_TO_THINGSPEAK = True
HR_DATA_LENGTH = 90

def create_hr_data(length):
    """Create a human-like heart rate time series."""
    # Set the length of the time series
    n = length

    # Generate a random heart rate time series with a mean of 70 bpm and standard deviation of 10 bpm
    heart_rate = np.random.normal(loc=70, scale=10, size=n)

    # Add some sinusoidal variation to simulate the natural variability of a human heart rate
    t = np.arange(0, n)
    sinusoidal_variation = 5 * np.sin(t * 2 * np.pi / 600)  # 10-second cycle
    heart_rate += sinusoidal_variation

    return heart_rate


def plot_hr_data(heart_rate):
    """Plot the heart rate time series."""
    plt.plot(heart_rate)
    plt.xlabel('Time (s)')
    plt.ylabel('Heart Rate (bpm)')
    plt.title('Human-like Heart Rate Time Series')
    plt.show()


async def auth_with_frisbee_server(websocket):
    """Authenticate with the Frisbee Server."""
    auth_credentials = {
        # 'admin_username': 'admin',
        'admin_password': ADMIN_PASSWORD,
        'participant_label': sys.argv[1],
    }

    await websocket.send(json.dumps(auth_credentials))

    auth_resp = await websocket.recv()

    if auth_resp == '{"status": "connected"}':
        print(f'[FRISBEE SERVER] {auth_resp}')
        print('Authenticated with Frisbee Server')
    else:
        print('Authentication with Frisbee Server failed')


async def consumer_handler(websocket):
    """Receive messages from the Frisbee Server."""
    async for message in websocket:
        print(f"[Frisbee Server] {message}]")


async def producer_handler(msg):
    """Send heart rate to ThingSpeak."""
    if 'config' in msg and SEND_DATA_TO_THINGSPEAK:
        msg = json.loads(msg)
        write_api_key = msg['config']['api_keys'][0]['api_key']
        heart_rate = create_hr_data(HR_DATA_LENGTH)

        async with aiohttp.ClientSession() as session:
            for hr in np.nditer(heart_rate):
                async with session.get(f'https://api.thingspeak.com/update?api_key={write_api_key}&field1={hr}') as resp:
                    print(f'Response Status {resp.status}')
                    # print(await resp.text())
                await asyncio.sleep(1)  # ThingSpeak API only allows 1 request per second.


async def handler():

    async with websockets.connect(URL) as ws:

        await auth_with_frisbee_server(ws)

        # Receive ThingSpeak channel settings from Frisbee Server
        msg = await ws.recv()  # {'config': ch_settings}
        print(f"[Frisbee Server] {msg}]")

        await asyncio.gather(
            consumer_handler(ws),
            producer_handler(msg),
        )


if __name__ == '__main__':
    asyncio.run(handler())
