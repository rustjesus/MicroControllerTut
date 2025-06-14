from machine import Pin, I2C, PWM
import neopixel
import ssd1306
import time
import ujson as json

# === Configuration ===
color_cycle_speed = 50  # NeoPixel cycle speed

# === GPIO LED Setup ===
led_pins = [Pin(pin, Pin.OUT) for pin in (20, 21, 22, 26, 27)]
button_pin = Pin(15, Pin.IN, Pin.PULL_UP)         # Start/stop button
reset_button_pin = Pin(13, Pin.IN, Pin.PULL_UP)   # Reset score button
num_leds_gpio = len(led_pins)
flickers_per_second = 3
interval = 1 / (flickers_per_second * num_leds_gpio)
check_interval = 0.01
current_led = 0
flicker_count = 0
running = False
prev_button_state = 1
prev_reset_state = 1

# === NeoPixel Setup ===
NUM_LEDS = 8
LED_PIN = 16
np = neopixel.NeoPixel(Pin(LED_PIN), NUM_LEDS)
hue_offset = 0

# === RGB LED Setup (PWM) ===
rgb_pins = {
    'r': PWM(Pin(2)),
    'g': PWM(Pin(3)),
    'b': PWM(Pin(4))
}
for pwm in rgb_pins.values():
    pwm.freq(1000)
rgb_hue = 0

# === OLED Setup ===
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# === Buzzer Setup ===
buzzer_pin = Pin(14, Pin.OUT)

# === Score File Handling ===
score_file = "score.json"

def load_score():
    try:
        with open(score_file, "r") as f:
            data = json.load(f)
            return data.get("wins", 0)
    except:
        return 0

def save_score(wins):
    with open(score_file, "w") as f:
        json.dump({"wins": wins}, f)

wins = load_score()
win_recorded = False

# === OLED Drawing ===
scroll_y = 0
scroll_direction = 1
scroll_text = "Playing Game"

def draw_score(w):
    score_text = f"W:{w}"
    x = oled_width - len(score_text) * 8
    y = oled_height - 10
    oled.text(score_text, x, y)

def lightText():
    oled.text("L:{}".format(current_led + 1), 0, oled_height - 10)

def scroll_oled_text(text):
    global scroll_y, scroll_direction
    oled.fill(0)
    oled.text(text, 0, scroll_y)
    lightText()
    draw_score(wins)
    oled.show()
    max_scroll_y = oled_height - 18
    scroll_y += scroll_direction * 2
    if scroll_y > max_scroll_y or scroll_y < 0:
        scroll_direction *= -1

# === NeoPixel & RGB Helpers ===
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

def set_rgb_color(r, g, b):
    rgb_pins['r'].duty_u16(int(r / 255 * 65535))
    rgb_pins['g'].duty_u16(int(g / 255 * 65535))
    rgb_pins['b'].duty_u16(int(b / 255 * 65535))

#single rbg
def update_rgb_cycle():
    global rgb_hue
    rgb_hue = (rgb_hue + 3) % 256
    r, g, b = wheel(rgb_hue)
    set_rgb_color(r, g, b)

def buzz(duration=0.2, frequency=1000):
    delay = 1 / (frequency * 2)
    cycles = int(duration * frequency)
    for _ in range(cycles):
        buzzer_pin.value(1)
        time.sleep(delay)
        buzzer_pin.value(0)
        time.sleep(delay)

# === Main Loop ===
print("Press button to start/stop flickering or reset score")

while True:
    button_state = button_pin.value()
    reset_state = reset_button_pin.value()

    if button_state == 0 and prev_button_state == 1:
        running = not running
        print("Button toggled! Running is now:", running)
        if running:
            set_strip_color((255, 0, 0))
            win_recorded = False
        time.sleep(0.2)
    prev_button_state = button_state

    if reset_state == 0 and prev_reset_state == 1:
        wins = 0
        save_score(wins)
        oled.fill(0)
        oled.text("Score Reset!", 0, 0)
        draw_score(wins)
        oled.show()
        time.sleep(0.5)
    prev_reset_state = reset_state

    if running:
        scroll_oled_text(scroll_text)
        led_pins[current_led].value(1)
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < interval * 1000:
            time.sleep(check_interval)
        for led in led_pins:
            led.value(0)
        current_led = (current_led + 1) % num_leds_gpio
        flicker_count += 1
        print(f"[{time.ticks_ms()} ms] Flicker #{flicker_count} - LED{current_led + 1} is ON")
    else:
        for i, led in enumerate(led_pins):
            led.value(1 if i == current_led else 0)

        oled.fill(0)
        if current_led == num_leds_gpio - 1:
            if not win_recorded:
                wins += 1
                save_score(wins)
                win_recorded = True
            oled.text("Game Won!", 0, 0)
            draw_score(wins)
            lightText()
            oled.show()
            rainbow_cycle(hue_offset)
            hue_offset = (hue_offset + color_cycle_speed) % 256
            buzz(0.5, 2000)
        else:
            win_recorded = False
            oled.text("Game Over :(", 0, 0)
            draw_score(wins)
            lightText()
            oled.show()
            set_strip_color((255, 0, 0))

        time.sleep(0.05)

    # Slowly cycle RGB LED
    update_rgb_cycle()

