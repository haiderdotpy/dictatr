import io
import select
import time

import evdev
from evdev import ecodes

from src.audio_capture import start_capture, stop_capture


HOTKEY = ecodes.KEY_RIGHTCTRL
MIN_HOLD_TIME = 0.2  # seconds


def find_keyboards():
    keyboards = []

    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)

        caps = dev.capabilities().get(ecodes.EV_KEY, [])

        if ecodes.KEY_A in caps:
            keyboards.append(dev)

    return keyboards


def wait_for_recording():
    """
    Blocks until the user performs one push-to-talk action.

    Does NOT grab devices — the hotkey event reaches both dictatr
    and the compositor. Right Ctrl is harmless as a standalone key.
    This keeps normal keyboard input working (including Ctrl+C).

    Returns:
        BytesIO containing WAV audio.
    """

    devices = find_keyboards()

    if not devices:
        raise RuntimeError("No keyboards found.")

    device_map = {d.fd: d for d in devices}

    recording = False
    press_time = None

    print("Waiting for hotkey...")

    while True:
        ready, _, _ = select.select(device_map, [], [])

        for fd in ready:
            device = device_map[fd]

            for event in device.read():

                if event.type != ecodes.EV_KEY:
                    continue

                if event.code != HOTKEY:
                    continue

                # Key pressed
                if event.value == 1 and not recording:
                    recording = True
                    press_time = time.monotonic()
                    start_capture()
                    print("Recording...")

                # Key released
                elif event.value == 0 and recording:
                    recording = False

                    duration = time.monotonic() - press_time

                    if duration < MIN_HOLD_TIME:
                        print("Ignored short press.")
                        continue

                    print(f"Recorded {duration:.2f}s")

                    return stop_capture()