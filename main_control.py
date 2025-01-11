import asyncio
import threading
from pynput import keyboard
from drone_connection import connect_drone
from drone_movement import DroneMovement
from obstacle_detection import detect_obstacle

# Define global dictionaries for movements and flags
movement = {"w": False, "a": False, "s": False, "d": False}
altitude_change = {"8": False, "2": False}
yaw_change = {"4": False, "6": False}
takeoff_flag = False
landing_flag = False
loop = None

# MAVSDK control coroutine
async def mavsdk_control():
    global loop, takeoff_flag, landing_flag
    loop = asyncio.get_event_loop()

    # Connect to the drone
    drone = await connect_drone()
    drone_movement = DroneMovement(drone)

    try:
        while True:
            if takeoff_flag:
                print("Attempting to take off...")
                try:
                    await drone_movement.takeoff()
                except Exception as e:
                    print(f"Takeoff failed: {e}")
                takeoff_flag = False

            if landing_flag:
                try:
                    await drone_movement.land()
                except Exception as e:
                    print(f"Landing failed: {e}")
                landing_flag = False

            # Update the drone's position based on key input
            await drone_movement.update_position(movement, altitude_change, yaw_change)

            # Check for obstacles
            obstacle_detected = await detect_obstacle(drone)
            if obstacle_detected:
                print("Obstacle detected! Taking safety measures.")
                # Handle obstacle (you can customize this behavior)

            # Reduce loop delay for smoother updates
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"An error occurred in mavsdk_control: {e}")

# Key press handler
def on_press(key):
    global takeoff_flag, landing_flag
    try:
        if key.char == "w":
            movement["w"] = True
        elif key.char == "s":
            movement["s"] = True
        elif key.char == "a":
            movement["a"] = True
        elif key.char == "d":
            movement["d"] = True
        elif key.char == "8":
            altitude_change["8"] = True
        elif key.char == "2":
            altitude_change["2"] = True
        elif key.char == "4":
            yaw_change["4"] = True
        elif key.char == "6":
            yaw_change["6"] = True
        elif key.char == "t":
            takeoff_flag = True
        elif key.char == "l":
            landing_flag = True
    except AttributeError:
        print(f"Unhandled key: {key}")

# Key release handler
def on_release(key):
    try:
        if key.char == "w":
            movement["w"] = False
        elif key.char == "s":
            movement["s"] = False
        elif key.char == "a":
            movement["a"] = False
        elif key.char == "d":
            movement["d"] = False
        elif key.char == "8":
            altitude_change["8"] = False
        elif key.char == "2":
            altitude_change["2"] = False
        elif key.char == "4":
            yaw_change["4"] = False
        elif key.char == "6":
            yaw_change["6"] = False
    except AttributeError:
        print(f"Unhandled key: {key}")

# Keyboard listener
def listen_for_keys():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Main coroutine
async def main():
    # Start the keyboard listener in a separate thread
    listener_thread = threading.Thread(target=listen_for_keys)
    listener_thread.start()

    # Start the MAVSDK control task
    control_task = asyncio.create_task(mavsdk_control())
    await control_task

if __name__ == "__main__":
    asyncio.run(main())
