#!/usr/bin/env python3

import evdev
import json
import sys


def get_config() -> dict:
    with open("config.json") as json_data_file:
        return json.load(json_data_file)


# Try to find the input device
try:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if 'gpio-keys' in device.phys:
            input_device = device
            print(f"Found the key at {device.path}")
            break
except Exception:
    print("Could not find a gpio-keys input device, make sure that the module "
          "has been loaded")
    sys.exit(1)

# We'll start reading from the device if we found it
time_keydown = 0
time_keyup = 0
index = 0

try:
    json_config = get_config()

    for event in device.read_loop():
        """TODO: The time calculation is always done, it should only be done
            if there's a down followed by an up event. But it should also
            differentiate between clicking once and clicking twice """
        if event.type == evdev.ecodes.EV_KEY:
            print(evdev.categorize(event))
            print(event.timestamp())
            keyevent = evdev.KeyEvent(event)
            # Store the key_up/down timestamps
            if keyevent.keystate == keyevent.key_down:
                time_keydown = event.timestamp() * 1000.0
            elif keyevent.keystate == keyevent.key_up:
                time_keyup = event.timestamp() * 1000.0

            total_pressed_time = time_keyup - time_keydown
            # TODO: This isn't working properly
            print(f"Key was pressed for {total_pressed_time} ms")
            if total_pressed_time > json_config["time"]["press"]:
                press_type = "long"
            elif total_pressed_time >= json_config["time"]["twice"]:
                press_type = "twice"
            else:
                press_type = "short"

            print(f"This was a {press_type} button press")

except KeyboardInterrupt:
    print("Keyboard interrupt, exiting")
