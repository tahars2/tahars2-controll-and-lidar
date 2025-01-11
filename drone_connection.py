# drone_connection.py

import asyncio
from mavsdk import System

async def connect_drone(system_address="udp://:14540"):
    """
    Connects to the drone using MAVSDK.
    """
    drone = System()
    await drone.connect(system_address=system_address)
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break
    return drone
