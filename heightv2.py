import RPi.GPIO as GPIO
import time
from collections import Counter

def gather_height():
    TRIG = 4
    ECHO = 17
    SPEED_OF_SOUND = 34300

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)

    def measure_distance():
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        pulse_start = time.time()
        timeout = pulse_start + 0.1  # 100ms timeout to prevent infinite loop

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                print("Echo timeout - no response from sensor")
                return None  # Return None if sensor is unresponsive

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                print("Echo timeout - no response from sensor")
                return None  

        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration * SPEED_OF_SOUND) / 2
        return round(distance, 2)

    print("Waiting for the sensor to settle...")
    time.sleep(2)

    max_retries = 3  # Maximum attempts before stopping

    for attempt in range(max_retries):
        results = []
        for _ in range(5):
            distance = measure_distance()
            if distance is None or distance >= 214:
                continue
            results.append(distance)
            print(f"Measurement {len(results)}: {distance} cm")
            time.sleep(1)

        if not results:
            print(f"Attempt {attempt+1}/{max_retries}: No valid measurements. Retrying...")
            continue

        integer_results = [int(d) for d in results]
        counter = Counter(integer_results)
        valid_integers = [k for k, v in counter.items() if v >= 2]

        if valid_integers:
            selected_integer = valid_integers[0]
            filtered_results = [d for d in results if int(d) == selected_integer]
            average_distance = round(sum(filtered_results) / len(filtered_results), 2)
            height = round(213.16 - average_distance, 2)
            print(f"Average distance for integer {selected_integer}: {average_distance} cm")
            print(f"Calculated height: {height} cm")
            GPIO.cleanup()
            return {"height": height}

        print(f"Attempt {attempt+1}/{max_retries}: No consistent measurements. Retrying...")

    print("Max retries reached. Unable to determine height.")
    GPIO.cleanup()
    return None  # Return None if no valid measurements after max retries

# Run the function
gather_height()
