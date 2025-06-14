from machine import Pin, I2C
import neopixel
import ssd1306
import time

color_cycle_speed = 50  # Adjust this value to make the color cycle faster or slower

# === GPIO LED Configuration ===
led_pins = [Pin(pin, Pin.OUT) for pin in (20, 21, 22, 26, 27)]
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

# === OLED Setup ===
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# === Passive Buzzer Setup ===
buzzer_pin = Pin(14, Pin.OUT)

# === OLED Scrolling State ===
scroll_y = 0
scroll_direction = 1
scroll_text = "Playing Game"

def scroll_oled_text(text):
    global scroll_y, scroll_direction
    oled.fill(0)
    # Draw scrolling text
    oled.text(text, 0, scroll_y)
    # Draw light number at fixed position
    light_num = current_led + 1
    oled.text("Light:{}".format(light_num), 0, oled_height - 10)
    oled.show()
    # Update scroll position with limits to avoid overlap
    max_scroll_y = oled_height - 18  # Prevent overlap with y=oled_height-10
    scroll_y += scroll_direction * 2
    if scroll_y > max_scroll_y or scroll_y < 0:
        scroll_direction *= -1


# === NeoPixel Helpers ===
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

def buzz(duration=0.2, frequency=1000):
    delay = 1 / (frequency * 2)
    cycles = int(duration * frequency)
    for _ in range(cycles):
        buzzer_pin.value(1)
        time.sleep(delay)
        buzzer_pin.value(0)
        time.sleep(delay)

# === Initial State ===
print("Press button to start/stop flickering")

# === Main Loop ===
while True:
    button_state = button_pin.value()
    if button_state == 0 and prev_button_state == 1:
        running = not running
        print("Button toggled! Running is now:", running)
        if running:
            set_strip_color((255, 0, 0))  # Set strip to red when game starts
        time.sleep(0.2)  # debounce

    prev_button_state = button_state

    if running:
        # Scroll text + show light number
        scroll_oled_text(scroll_text)

        # Turn on current GPIO LED
        led_pins[current_led].value(1)
        start_time = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start_time) < interval * 1000:
            time.sleep(check_interval)

        # Turn off all GPIO LEDs
        for led in led_pins:
            led.value(0)

        # Advance to next LED
        current_led = (current_led + 1) % num_leds_gpio
        flicker_count += 1
        print(f"[{time.ticks_ms()} ms] Flicker #{flicker_count} - LED{current_led + 1} is ON")
    else:
        # Game stopped: indicate current LED stays lit
        for i, led in enumerate(led_pins):
            led.value(1 if i == current_led else 0)

        if current_led == num_leds_gpio - 1:
            # Won
            oled.fill(0)
            oled.text("Game Won!", 0, 0)
            # Show light number
            oled.text("Light:{}".format(current_led + 1), 0, oled_height - 10)
            oled.show()
            rainbow_cycle(hue_offset)
            hue_offset = (hue_offset + color_cycle_speed) % 256
            buzz(0.5, 2000)  # Buzz for 0.5 seconds at 2kHz
        else:
            # Game over
            oled.fill(0)
            oled.text("Game Over :(", 0, 0)
            oled.text("Light:{}".format(current_led + 1), 0, oled_height - 10)
            oled.show()
            set_strip_color((255, 0, 0))  # Red

        time.sleep(0.05)

