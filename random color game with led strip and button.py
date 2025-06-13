from machine import Pin
import time
import neopixel

#THIS USES THE LED STRIP AS A OUTPUT FOR "WINNING" IF THE GAME ENDS ON THE LAST LIGHT THE LED STRIP CHANGES TO MULTI COLOR INSTEAD OF RED.
# === GPIO LED Configuration ===
led_pins = [
    Pin(20, Pin.OUT),
    Pin(21, Pin.OUT),
    Pin(22, Pin.OUT),
    Pin(26, Pin.OUT),
    Pin(27, Pin.OUT)  # Last LED
]
button_pin = Pin(15, Pin.IN, Pin.PULL_UP)
num_leds_gpio = len(led_pins)
flickers_per_second = 3
interval = 1 / (flickers_per_second * num_leds_gpio)
check_interval = 0.01
current_led = 0
flicker_count = 0
running = False
prev_button_state = 1

# === NeoPixel Configuration ===
NUM_LEDS = 8
LED_PIN = 16
np = neopixel.NeoPixel(Pin(LED_PIN), NUM_LEDS)
hue_offset = 0

# === Helper Functions ===
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

def set_strip_color(color):
    for i in range(NUM_LEDS):
        np[i] = color
    np.write()

# === Initial Message ===
print("Press button to start/stop flickering")

# === Main Loop ===
while True:
    button_state = button_pin.value()
    if button_state == 0 and prev_button_state == 1:
        running = not running
        print("Button toggled! Running is now:", running)
        time.sleep(0.2)  # debounce

    prev_button_state = button_state

    if running:
        # Turn on current LED
        led_pins[current_led].value(1)
        start_time = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start_time) < interval * 1000:
            time.sleep(check_interval)

        # Turn off all LEDs
        for led in led_pins:
            led.value(0)

        # Advance LED
        current_led = (current_led + 1) % num_leds_gpio
        flicker_count += 1
        print(f"[{time.ticks_ms()} ms] Flicker #{flicker_count} - LED{current_led + 1} is ON")
    else:
        # Pause state: keep current LED lit
        for i, led in enumerate(led_pins):
            led.value(1 if i == current_led else 0)

        # Show color on NeoPixel strip based on current LED
        if current_led == num_leds_gpio - 1:  # If on last LED (Pin 27)
            rainbow_cycle(hue_offset)
            hue_offset = (hue_offset + 5) % 256  # Rainbow speed
        else:
            set_strip_color((255, 0, 0))  # Solid red

        time.sleep(0.05)
