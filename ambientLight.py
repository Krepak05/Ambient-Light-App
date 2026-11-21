import argparse
import time
import mss
import numpy as np
from monitorcontrol import get_monitors


# The settings of selected area
HEIGHT = 100 
WIDTH = 500
INTERVAL_SECONDS = 0.05
MIN_WRITE_INTERVAL = 0.1
SMOOTHING = 0.3

#After running findYourMonitor.py and finding the name given for your wanted monitor at marked "#<<<<<<<<<<<<<<HERE 1.0" you will find
#change the value of "theVictim" to name of wanted monitor with ambient light

theVictim = "omen x 25f" #<<<<<<<<<<<<<<HERE 1.0

def monitorFunction():
    for monitor in get_monitors():
        try:
            with monitor:
                caps = monitor.get_vcp_capabilities()
            if theVictim in caps.get("model", "").lower():  
                return monitor
        except Exception:
            continue
    raise RuntimeError(f"{theVictim} is not found with DDC/CI.")

def sample_bottom_rgb(sct, display):               #<<<<<<<<<<<<<<<<<<<<<< This is a very important Part, it scans the color near your 
    scan_height = min(HEIGHT, display["height"])   #Ambient light displayed on your monitor and then selecting the color of the ligth

    scan_width = min(WIDTH, display["width"])

    rectangle = {                      # This here is the analyised area
        "left": display["left"] + (display["width"] - scan_width) // 2,
        "top": display["top"] + display["height"] - scan_height,
        "width": scan_width,
        "height": scan_height,
    }
    
    screenshot = sct.grab(rectangle)

    pixels = np.frombuffer(
        screenshot.rgb, dtype=np.uint8
    ).reshape(scan_height, scan_width, 3)

    sample = pixels[::4, ::4].reshape(-1, 3).astype(float) #Takes the sample 

    maximum = sample.max(axis=1) #This finds the colors of the pixels
    minimum = sample.min(axis=1)

    mask = (maximum >= 40) & ((maximum - minimum) >= 35)  # This part is for vibrance to make the color display much livelier to not
                                                           # get washed out colors
    if np.any(mask):
        average = sample[mask].mean(axis=0)
        gray = average.mean()
        average = gray + (average - gray) * 1.6
    else:
        average = sample.mean(axis=0) * 0.2     
    average = np.clip(average, 0, 255)
    return tuple(int(round(x)) for x in average)


def run(monitor, screen_number):
    channels = (0xE5, 0xE8, 0xEA)

    with mss.mss() as sct:
        if not 1 <= screen_number < len(sct.monitors):
            raise ValueError("Display does not exist")

        display = sct.monitors[screen_number]

        print(f"{theVictim} - RGB Ambilight")
        print("Scanning the pixels")
        print("Ctrl+C to shut down the program.\n")

        with monitor:
            # load starting RGB
            last_rgb = [
                monitor.vcp.get_vcp_feature(code)[0]
                for code in channels
            ]

            if not all(0 <= v <= 255 for v in last_rgb):
                raise RuntimeError("Unexpected RGB")

            last_write = 0.0
            smoothed = None

            try:
                while True:
                    rgb = sample_bottom_rgb(sct, display)

                    values = np.array(rgb, dtype=float)

                    if smoothed is None:
                        smoothed = values
                    else:
                        smoothed = (
                            SMOOTHING * values
                            + (1 - SMOOTHING) * smoothed
                        )

                    target = [
                        int(np.clip(round(v), 0, 255))
                        for v in smoothed
                    ]

                    now = time.monotonic()

                    if now - last_write >= MIN_WRITE_INTERVAL:
                        changed = False

                        for i, code in enumerate(channels):
                            if abs(target[i] - last_rgb[i]) >= 8: #small changes get ignored
                                try:
                                    monitor.vcp.set_vcp_feature(code, target[i])
                                    last_rgb[i] = target[i]
                                    changed = True
                                except Exception:
                                    pass

                        if changed:
                            last_write = time.monotonic()

                            print(
                                f"RGB -> {tuple(last_rgb)}"
                            )

                    time.sleep(INTERVAL_SECONDS)

            except KeyboardInterrupt:
                print("\nAmbilight stopped.")


def main():
    parser = argparse.ArgumentParser(description="Ambilight for Monitor")
    parser.add_argument("--screen", type=int, default=1, help="Number assigned to monitor (Normaly 1)")
    args = parser.parse_args()
    monitor = monitorFunction()
    run(monitor, args.screen)


if __name__ == "__main__":
    main()
