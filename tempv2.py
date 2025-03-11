import board
import busio as io
import adafruit_mlx90614
from time import sleep

# Function to apply emissivity correction
def correct_temperature(measured_temp, ambient_temp, emissivity):
    """
    Corrects the temperature measurement based on emissivity.
    
    Parameters:
    - measured_temp (float): Measured temperature in Celsius.
    - ambient_temp (float): Ambient temperature in Celsius.
    - emissivity (float): Emissivity of the object.
    
    Returns:
    - float: Corrected object temperature in Celsius.
    """
    if not (0 < emissivity <= 1):
        raise ValueError("Emissivity must be between 0 and 1.")

    # Convert Celsius to Kelvin
    measured_temp_K = measured_temp + 273.15
    ambient_temp_K = ambient_temp + 273.15

    # Apply the emissivity correction formula
    T_measured_4 = measured_temp_K ** 4
    T_ambient_4 = ambient_temp_K ** 4
    T_object_4 = (T_measured_4 - (1 - emissivity) * T_ambient_4) / emissivity

    # Convert back to Celsius
    corrected_temp_C = (T_object_4 ** 0.25) - 273.15

    return corrected_temp_C

# Initialize I2C and MLX90614 sensor
i2c = io.I2C(board.SCL, board.SDA, frequency=100000)
mlx = adafruit_mlx90614.MLX90614(i2c)

sleep(2)  # Allow sensor to stabilize

# Read raw temperatures from sensor
ambient_temp = mlx.ambient_temperature
target_temp = mlx.object_temperature

# Define emissivity (human skin is between 0.95 and 0.98)
emissivity = 0.97  # Adjust as needed

# Apply emissivity correction
corrected_temp = correct_temperature(target_temp, ambient_temp, emissivity)

# Print results
print(f"Ambient Temperature: {ambient_temp:.2f} °C")
print(f"Target Temperature (Raw): {target_temp:.2f} °C")
print(f"Target Temperature (Corrected): {corrected_temp:.2f} °C")
