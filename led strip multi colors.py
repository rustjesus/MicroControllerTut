from machine import Pin
import time
import neopixel

# === Configuration ===
NUM_LEDS = 8
LED_PIN = 16
BUTTON_PIN = 15

np = neopixel.NeoPixel(Pin(LED_PIN), NUM_LEDS)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

hue_offset = 0
prev_button_state = 1

# Define speeds: 0 = stopped, others are animation speeds
speed_options = [0, 5, 50, 100]  # Adjust as needed (0 = stopped, 20 = fast)
speed_index = 0  # Start in stopped state

# Helper: Convert hue (0-255) to RGB
def wheel(pos):
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

def rainbow_cycle(offset):
    for i in range(NUM_LEDS):
        pixel_index = (i * 256 // NUM_LEDS + offset) % 256
        np[i] = wheel(pixel_index)
    np.write()

print("Press button to cycle speed: Stopped -> Slow -> Medium -> Fast")

while True:
    button_state = button.value()

    if button_state == 0 and prev_button_state == 1:
        speed_index = (speed_index + 1) % len(speed_options)
        print(f"Button pressed. Speed index: {speed_index}, Speed: {speed_options[speed_index]}")
        time.sleep(0.2)  # debounce

    prev_button_state = button_state

    current_speed = speed_options[speed_index]

    if current_speed > 0:
        rainbow_cycle(hue_offset)
        hue_offset = (hue_offset + current_speed) % 256
    # Even when stopped, keep writing the last frame to hold the LEDs steady
    np.write()
    time.sleep(0.05)

