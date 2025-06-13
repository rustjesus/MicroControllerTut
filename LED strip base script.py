from machine import Pin
import time
import neopixel

# === Configuration ===
NUM_LEDS = 8               # Number of LEDs on your strip
LED_PIN = 16                # GPIO pin connected to the strip
BUTTON_PIN = 15             # GPIO pin connected to button
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

np = neopixel.NeoPixel(Pin(LED_PIN), NUM_LEDS)

running = False
prev_button_state = 1

# Define some basic colors
colors = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (0, 255, 255),  # Cyan
    (255, 0, 255),  # Magenta
    (255, 255, 255) # White
]

color_index = 0

def fill_color(color):
    for i in range(NUM_LEDS):
        np[i] = color
    np.write()

print("Press button to toggle LED animation")

while True:
    button_state = button.value()
    
    # Toggle animation on button press (falling edge)
    if button_state == 0 and prev_button_state == 1:
        running = not running
        print("Button pressed! Running:", running)
        time.sleep(0.001)  # debounce

    prev_button_state = button_state

    if running:
        fill_color(colors[color_index])
        color_index = (color_index + 1) % len(colors)
        time.sleep(0.5)
    else:
        fill_color(colors[color_index])  # Hold last color
        time.sleep(0.05)
