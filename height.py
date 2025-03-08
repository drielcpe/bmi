import RPi.GPIO as GPIO
import time
from collections import Counter
def gather_height():
    TRIG = 23
    ECHO = 24
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

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start

        distance = (pulse_duration * SPEED_OF_SOUND) / 2
        return round(distance, 2)

    print("Waiting for the sensor to settle")
    time.sleep(2)

    while True:
        distance = measure_distance()
        if distance <= 200:
            break
        print(f"Distance {distance} cm is too large. Retrying...")
        time.sleep(1)  

    while True:
        results = []
        for _ in range(5):
            distance = measure_distance()
            results.append(distance)
            print(f"Measurement {len(results)}: {distance} cm")
            time.sleep(1)

        integer_results = [int(d) for d in results]

        counter = Counter(integer_results)

        valid_integers = [k for k, v in counter.items() if v >= 2]

        if valid_integers:
            selected_integer = valid_integers[0]
            filtered_results = [d for d in results if int(d) == selected_integer]
            average_distance = round(sum(filtered_results) / len(filtered_results), 2)
            print(f"Average distance for integer {selected_integer}: {average_distance} cm")
            print(f"height: {213.16-average_distance} cm")
            GPIO.cleanup()
            return {
                "height":  f"213.16-{average_distance}"
            }
        else:
            print("No two measurements share the same integer. Re-gathering...")

gather_height()