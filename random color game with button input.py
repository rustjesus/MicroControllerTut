from machine import Pin
import time

# === Configuration ===
flickers_per_second = 3
led_pins = [
    Pin(20, Pin.OUT),
    Pin(21, Pin.OUT),
    Pin(22, Pin.OUT),
    Pin(26, Pin.OUT),
    Pin(27, Pin.OUT)
]
button_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # GPIO15 with internal pull-up

num_leds = len(led_pins)
interval = 1 / (flickers_per_second * num_leds)
check_interval = 0.01  # 10ms

flicker_count = 0
current_led = 0
running = False  # Start in stopped state
prev_button_state = 1  # Assume unpressed initially (pull-up logic)

# === Initial Message ===
print("Press button to start game")

# === Main Loop ===
while True:
    # Check for button press (transition from high to low)
    button_state = button_pin.value()
    if button_state == 0 and prev_button_state == 1:  # Button just pressed
        running = not running  # Toggle running state
        print("Button toggled! Running is now:", running)
        time.sleep(0.2)  # Simple debounce delay

    prev_button_state = button_state  # Update previous button state

    if running:
        led_pins[current_led].value(1)
        start_time = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start_time) < interval * 1000:
            time.sleep(check_interval)

        for led in led_pins:
            led.value(0)

        current_led = (current_led + 1) % num_leds
        flicker_count += 1
        print(f"[{time.ticks_ms()} ms] Flicker #{flicker_count} - LED{current_led + 1} is ON")
    else:
        # Light stays on at current LED
        for i, led in enumerate(led_pins):
            led.value(1 if i == current_led else 0)
        time.sleep(0.05)
