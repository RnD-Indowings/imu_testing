from mpu9250_jmdev.mpu_9250 import MPU9250
import board
import busio
import adafruit_bmp280
import time

# -----------------------------
# Initialize MPU6500 (Accel + Gyro)
# -----------------------------
mpu = MPU9250(
    address_mpu_master=0x68,
    address_mpu_slave=0x68,
    bus=1,
    gfs=0x00,
    afs=0x00
)
print("Initializing MPU6500 (Accel + Gyro)...")

try:
    mpu.calibrateAccelerometer()
except:
    print("Accel calibration skipped.")
try:
    mpu.calibrateGyro()
except:
    print("Gyro calibration skipped.")

mpu.configure()
print("MPU6500 ready.\n")

# -----------------------------
# Initialize BMP280 (Adafruit)
# -----------------------------
i2c = busio.I2C(board.SCL, board.SDA)
bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)
print("BMP280 barometer ready.\n")

# -----------------------------
# Main loop
# -----------------------------
while True:
    accel = mpu.readAccelerometerMaster()
    gyro = mpu.readGyroscopeMaster()
    temperature = bmp.temperature
    pressure = bmp.pressure
    altitude = bmp.altitude

    print("----------------------------------")
    print(f"ACCEL (g): {accel}")
    print(f"GYRO  (°/s): {gyro}")
    print(f"TEMP (°C): {temperature:.2f}")
    print(f"PRESSURE (hPa): {pressure:.2f}")
    print(f"ALTITUDE (m): {altitude:.2f}")

    time.sleep(0.2)
