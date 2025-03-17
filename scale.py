import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
referenceUnit = 20.22
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()
weight = hx.get_weight(5)
weight = f"{weight/1000:.2f}"

print(weight)