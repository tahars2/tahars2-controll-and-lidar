import asyncio

DOWN_DISTANCE = 20.0  # Increased safe distance to 20 meters

async def detect_obstacle(drone):
    """
    Monitors the distance sensor to detect obstacles.
    Returns True if an obstacle is detected within the SAFE_DISTANCE.
    """
    async for distance_sensor in drone.telemetry.distance_sensor():
        if distance_sensor.current_distance_m < DOWN_DISTANCE:
            print(f"Obstacle detected at {distance_sensor.current_distance_m:.2f} meters!")
            return True
        await asyncio.sleep(0.1)  # Adjust sampling rate as needed
    return False

FORWARD_DISTANCE = 2.0  

async def detect_obstacle(drone):
    """
    Monitors the distance sensor to detect obstacles.
    Returns True if an obstacle is detected within the SAFE_DISTANCE.
    """
    async for distance_sensor in drone.telemetry.distance_sensor():
        if distance_sensor.current_distance_m < FORWARD_DISTANCE:
            print(f"Obstacle detected at {distance_sensor.current_distance_m:.2f} meters!")
            return True
        await asyncio.sleep(0.1)  # Adjust sampling rate as needed
    return False
