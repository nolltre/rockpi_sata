#!/usr/bin/env python3

import evdev

# Try to find the input device
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    if 'gpio-keys' in device.phys:
        input_device = device
        print(f"Found the key at {device.path}")
        break

if not input_device:
    print("Could not find a gpio-keys input device, make sure that the module "
          "has been loaded")

# We'll start reading from the device if we found it
time_keydown = 0
time_keyup = 0
index = 0

try:
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            print(evdev.categorize(event))
            print(event.timestamp())
            keyevent = evdev.KeyEvent(event)
            # Store the key_up/down timestamps
            if keyevent.keystate == keyevent.key_down:
                time_keydown = event.timestamp() * 1000.0
            elif keyevent.keystate == keyevent.key_up:
                time_keyup = event.timestamp() * 1000.0
            print(f"Key was pressed for {time_keyup-time_keydown} ms")

except KeyboardInterrupt:
    print("Keyboard interrupt, exiting")
