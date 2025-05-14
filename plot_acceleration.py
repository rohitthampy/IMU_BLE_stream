import asyncio
import threading
import time
import struct
from queue import Queue

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from bleak import BleakScanner, BleakClient

TIME_PERIOD = 0.05  # In Seconds

SERVICE_UUID = "082b91ae-e83c-11e8-9f32-f2801f1b9fd1"
accelX_UUID = "082b9438-e83c-11e8-9f32-f2801f1b9fd1"
accelY_UUID = "082b9622-e83c-11e8-9f32-f2801f1b9fd1"
accelZ_UUID = "082b976c-e83c-11e8-9f32-f2801f1b9fd1"

queue = Queue()
exit_event = threading.Event()

# Data storage
xs = []
y_vals = []
z_vals = []
x_vals = []
START_TIME = time.time()


async def accelx_handler(sender, data):
    x = struct.unpack('<f', data)[0]
    timestamp = round(time.time() - START_TIME, 2)
    queue.put((timestamp, x, None, None))


async def accely_handler(sender, data):
    y = struct.unpack('<f', data)[0]
    timestamp = round(time.time() - START_TIME, 2)
    queue.put((timestamp, None, y, None))


async def accelz_handler(sender, data):
    z = struct.unpack('<f', data)[0]
    timestamp = round(time.time() - START_TIME, 2)
    queue.put((timestamp, None, None, z))


async def ble_routine():
    print("Scanning for BLE devices....")
    devices = await BleakScanner.discover()

    target_device = None
    for d in devices:
        if d.name == "IMU_BLE":
            target_device = d
            break

    if not target_device:
        print("Device not found")
        return

    print(f"Connecting to {target_device.name} with address {target_device.address}")

    async with BleakClient(target_device.address) as client:
        print("Connected")

        await client.start_notify(accelX_UUID, accelx_handler)
        await client.start_notify(accelY_UUID, accely_handler)
        await client.start_notify(accelZ_UUID, accelz_handler)

        while not exit_event.is_set():
            await asyncio.sleep(TIME_PERIOD)

        print("Disconnecting BLE...")
        await client.stop_notify(accelX_UUID)
        await client.stop_notify(accelY_UUID)
        await client.stop_notify(accelZ_UUID)


def ble_thread():
    try:
        asyncio.run(ble_routine())
    except Exception as e:
        print(f"BLE thread error: {e}")


def animate(i):
    while not queue.empty():
        timestamp, x, y, z = queue.get()
        if timestamp not in xs:
            xs.append(timestamp)
            if x is not None:
                x_vals.append(x)
            else:
                x_vals.append(x_vals[-1] if x_vals else 0)

            if y is not None:
                y_vals.append(y)
            else:
                y_vals.append(y_vals[-1] if y_vals else 0)

            if z is not None:
                z_vals.append(z)
            else:
                z_vals.append(z_vals[-1] if z_vals else 0)

    ax.clear()
    ax.plot(xs, x_vals, label='X')
    ax.plot(xs, y_vals, label='Y')
    ax.plot(xs, z_vals, label='Z')
    ax.set_title("Acceleration Over Time")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Acceleration (m/s²)")
    ax.legend(loc='upper right')


# Setup plot
fig, ax = plt.subplots()
anim = animation.FuncAnimation(fig, animate, interval=TIME_PERIOD * 1000, cache_frame_data=False)

# Run BLE in background
thread = threading.Thread(target=ble_thread)
thread.start()

try:
    plt.show()
except KeyboardInterrupt:
    print("Keyboard interrupt received.")
finally:
    exit_event.set()
    thread.join()
    print("Program exited cleanly.")
