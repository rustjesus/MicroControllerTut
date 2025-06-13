from machine import Pin
import time

# === Configuration ===
flickers_per_second = 2  # Full back-and-forth cycles per second

led1 = Pin(20, Pin.OUT)  # Connect LED 1 to GPIO 20
led2 = Pin(21, Pin.OUT)  # Connect LED 2 to GPIO 21

interval = 1 / (flickers_per_second * 2)  # Each toggle is half a cycle (LED1 -> LED2 or LED2 -> LED1)

last_toggle_time = time.ticks_ms()
flicker_count = 0
current_led = 1  # Start with LED1

# === Initialize ===
led1.on()
led2.off()

# === Main Loop ===
while True:
    now = time.ticks_ms()

    if time.ticks_diff(now, last_toggle_time) >= interval * 1000:
        # Toggle between LEDs
        if current_led == 1:
            led1.off()
            led2.on()
            current_led = 2
        else:
            led2.off()
            led1.on()
            current_led = 1

        flicker_count += 0.5
        print(f"[{now} ms] Flicker #{int(flicker_count)} - LED{current_led} is ON")

        last_toggle_time = now
