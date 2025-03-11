import board
import busio as io
import adafruit_mlx90614
import time
import math

# Initialize I2C communication
i2c = io.I2C(board.SCL, board.SDA, frequency=100000)
mlx = adafruit_mlx90614.MLX90614(i2c)

# Set emissivity for human skin
EMISSIVITY = 0.98  # Try increasing this
OFFSET = 2.0       # Manual correction if needed

def celsius_to_kelvin(temp_c):
    """Convert Celsius to Kelvin."""
    return temp_c + 273.15

def kelvin_to_celsius(temp_k):
    """Convert Kelvin to Celsius."""
    return temp_k - 273.15

def correct_temperature(object_temp_c, ambient_temp_c, emissivity):
    """Apply emissivity correction formula."""
    Ta = celsius_to_kelvin(ambient_temp_c)
    Tom = celsius_to_kelvin(object_temp_c)
    
    # Compute corrected temperature
    Toc = math.pow(((math.pow(Tom, 4) - math.pow(Ta, 4)) / emissivity) + math.pow(Ta, 4), 0.25)
    
    # Convert back to Celsius
    return kelvin_to_celsius(Toc)

time.sleep(2)  # Allow sensor to stabilize

# Read temperatures
ambient_temp_c = mlx.ambient_temperature
object_temp_c = mlx.object_temperature

# Apply emissivity correction
corrected_temp_c = correct_temperature(object_temp_c, ambient_temp_c, EMISSIVITY)

# Apply manual offset correction if needed
final_temp_c = corrected_temp_c + OFFSET

# Print results
print(f"Ambient Temperature: {ambient_temp_c:.2f} °C")
print(f"Measured Object Temperature: {object_temp_c:.2f} °C")
print(f"Corrected Object Temperature: {corrected_temp_c:.2f} °C")
print(f"Final Adjusted Temperature: {final_temp_c:.2f} °C (with offset)")
