import asyncio
import math
from mavsdk.offboard import PositionNedYaw


class DroneMovement:
    def __init__(self, drone):
        self.drone = drone
        self.velocity = 30.0  # Velocity in meters per second
        self.altitude = -5.0  # Default altitude (NED coordinates, negative for above ground)
        self.yaw = 0.0
        self.x, self.y = 0.0, 0.0  # Initial position
        self.smoothing_factor = 0.2  # Smoothing factor for gradual movement

    async def takeoff(self):
        """
        Arms the drone and initiates takeoff.
        """
        print("Taking off...")
        await self.drone.action.arm()
        await self.drone.action.takeoff()
        await asyncio.sleep(10)
        print("Starting offboard mode...")
        await self.drone.offboard.set_position_ned(PositionNedYaw(self.x, self.y, self.altitude, self.yaw))
        await self.drone.offboard.start()

    async def land(self):
        """
        Lands the drone.
        """
        print("Landing...")
        await self.drone.action.land()
        await asyncio.sleep(10)

    async def update_position(self, movement, altitude_change, yaw_change):
        """
        Updates the drone's position based on the input keys, considering the current yaw angle.
        """
        # Calculate target positions and angles
        target_altitude = self.altitude
        target_yaw = self.yaw

        # Proportional movement based on key input (local frame)
        step = self.velocity * 0.3 # Smaller step size for finer control
        forward = 0.0
        right = 0.0

        if movement["w"]:
            forward += step
        if movement["s"]:
            forward -= step
        if movement["a"]:
            right -= step
        if movement["d"]:
            right += step

        # Transform local movement to global frame using current yaw
        target_x = self.x + (forward * math.cos(math.radians(self.yaw)) - right * math.sin(math.radians(self.yaw)))
        target_y = self.y + (forward * math.sin(math.radians(self.yaw)) + right * math.cos(math.radians(self.yaw)))

        # Altitude changes
        if altitude_change["8"]:
            target_altitude -= 0.9  # Fine altitude adjustment
        if altitude_change["2"]:
            target_altitude += 0.9

        # Yaw changes
        if yaw_change["4"]:
            target_yaw -= 10.0
        if yaw_change["6"]:
            target_yaw += 10.0

        # Smooth the position updates using a weighted average
        self.x = (1 - self.smoothing_factor) * self.x + self.smoothing_factor * target_x
        self.y = (1 - self.smoothing_factor) * self.y + self.smoothing_factor * target_y
        self.altitude = (1 - self.smoothing_factor) * self.altitude + self.smoothing_factor * target_altitude
        self.yaw = (1 - self.smoothing_factor) * self.yaw + self.smoothing_factor * target_yaw

        # Send position commands at higher frequency
        try:
            await self.drone.offboard.set_position_ned(
                PositionNedYaw(self.x, self.y, self.altitude, self.yaw)
            )
        except Exception as e:
            print(f"Failed to send position command: {e}")

        # Faster updates for smoother motion
        await asyncio.sleep(0.01)
