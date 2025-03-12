
import board
import busio as io
import adafruit_mlx90614
from time import sleep
i2c = io.I2C(board.SCL, board.SDA, frequency=100000)
mlx = adafruit_mlx90614.MLX90614(i2c)
sleep(2)
ambientTemp = "{:.2f}".format(mlx.ambient_temperature)
targetTemp = "{:.2f}".format(mlx.object_temperature)
print("Ambient Temperature:", ambientTemp, "°C")
print("Target Temperature:", targetTemp,"°C")
newtargetTemp = 0.9844 * mlx.object_temperature + 3.8967
print("Target Temperature with formula: {:.2f}".format(newtargetTemp))
deepseekformula = (1.513* mlx.object_temperature)-12.993
print("Target Temperature with formula: {:.2f}".format(deepseekformula))