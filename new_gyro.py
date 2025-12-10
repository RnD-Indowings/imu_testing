from mpu9250_jmdev.mpu_9250 import MPU9250
from smbus import SMBus
import time

# -------------------------------------------------
# Disable magnetometer functions completely
# -------------------------------------------------
MPU9250.configureAK8963 = lambda self, *args, **kwargs: None
MPU9250.calibrateAK8963 = lambda self, *args, **kwargs: None
MPU9250.readMagnetometer = lambda self: (0, 0, 0)

# -------------------------------------------------
# Initialize MPU9250 (Accel + Gyro only)
# -------------------------------------------------
mpu = MPU9250(
    address_ak=0x0C,              # ignored since mag disabled
    address_mpu_master=0x68,
    address_mpu_slave=0x68,
    bus=1,
    gfs=0x00,   # gyro ±250 dps
    afs=0x00,   # accel ±2g
    mfs=0x01,   # magnetometer unused
    mode=0x02   # MPU mode
)

print("Initializing MPU9250 (Accel + Gyro)...")

# -------------------------------------------------
# Calibrate accelerometer and gyroscope
# -------------------------------------------------
try:
    mpu.calibrateAccelerometer()
except Exception:
    print("Accel calibration skipped.")

try:
    mpu.calibrateGyro()
except Exception:
    print("Gyro calibration skipped.")

# -------------------------------------------------
# Apply configuration
# -------------------------------------------------
mpu.configure()
print("MPU9250 ready (Accel + Gyro)\n")

# -------------------------------------------------
# Main loop: read master (internal) accel/gyro
# -------------------------------------------------
while True:
    accel = mpu.readAccelerometerMaster()
    gyro  = mpu.readGyroscopeMaster()

    print("ACCEL (g):", accel)
    print("GYRO  (°/s):", gyro)
    print("----------------------------------")

    time.sleep(0.1)
