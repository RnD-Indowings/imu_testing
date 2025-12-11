# mpu9250_mag_i2c_master.py

import smbus2
import time
from mpu9250 import mpu9250

# I2C addresses
MPU9250_ADDR = 0x68       # MPU9250 device address
AK8963_ADDR = 0x0C        # Magnetometer address (used by MPU9250 internally)

# MPU9250 registers
PWR_MGMT_1 = 0x6B
USER_CTRL = 0x6A
I2C_MST_CTRL = 0x24
I2C_SLV0_ADDR = 0x25
I2C_SLV0_REG = 0x26
I2C_SLV0_CTRL = 0x27
EXT_SENS_DATA_00 = 0x49

# Magnetometer registers
AK8963_XOUT_L = 0x03
AK8963_CNTL1 = 0x0A

# Initialize I2C bus
bus = smbus2.SMBus(1)


def mpu9250_init():
    """Initialize MPU9250 and enable I2C master for AK8963 reads."""
    # Wake up MPU9250
    bus.write_byte_data(MPU9250_ADDR, PWR_MGMT_1, 0x00)
    time.sleep(0.1)

    # Enable I2C master mode
    bus.write_byte_data(MPU9250_ADDR, USER_CTRL, 0x20)  # I2C_MST_EN
    time.sleep(0.1)

    # Set I2C master clock
    bus.write_byte_data(MPU9250_ADDR, I2C_MST_CTRL, 0x0D)  # 400 kHz
    time.sleep(0.1)

    # Set AK8963 to continuous measurement mode 2 (100 Hz)
    write_mag_register(AK8963_CNTL1, 0x16)
    time.sleep(0.1)


def write_mag_register(reg, value):
    """Write a register on AK8963 via MPU9250 I2C master."""
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_ADDR, AK8963_ADDR)  # write mode
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_REG, reg)
    
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_CTRL, 0x81)  # enable, 1 byte
    time.sleep(0.01)


def read_mag_data():
    """Read raw magnetometer data via MPU9250 EXT_SENS_DATA registers."""
    # Configure MPU9250 I2C master to read 7 bytes from AK8963 starting at XOUT_L
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_ADDR, AK8963_ADDR | 0x80)  # read mode
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_REG, AK8963_XOUT_L)
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_CTRL, 0x87)  # enable, 7 bytes
    time.sleep(0.01)

    # Wait for data ready by reading ST1
    for _ in range(10):
        bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_ADDR, AK8963_ADDR | 0x80)
        bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_REG, 0x02)  # ST1 register
        bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_CTRL, 0x81)
        st1 = bus.read_byte_data(MPU9250_ADDR, EXT_SENS_DATA_00)
        if st1 & 0x01:  # Data ready
            break
        time.sleep(0.01)

    # Read 7 bytes from EXT_SENS_DATA_00
    data = [bus.read_byte_data(MPU9250_ADDR, EXT_SENS_DATA_00 + i) for i in range(7)]

    # Convert to signed 16-bit values
    x = (data[1] << 8) | data[0]
    y = (data[3] << 8) | data[2]
    z = (data[5] << 8) | data[4]
    x = x - 0x10000 if x >= 0x8000 else x
    y = y - 0x10000 if y >= 0x8000 else y
    z = z - 0x10000 if z >= 0x8000 else z

    return x, y, z


if __name__ == "__main__":
    mpu9250_init()
    time.sleep(0.1)

    x, y, z = read_mag_data()
    print("Raw Magnetometer:", x, y, z)
