# mpu9250_mag_full.py

import smbus2
import time

# I2C addresses
MPU9250_ADDR = 0x68
AK8963_ADDR = 0x0C

# MPU9250 registers
PWR_MGMT_1 = 0x6B
USER_CTRL = 0x6A
I2C_MST_CTRL = 0x24
I2C_SLV0_ADDR = 0x25
I2C_SLV0_REG = 0x26
I2C_SLV0_CTRL = 0x27
I2C_SLV0_DO = 0x63
EXT_SENS_DATA_00 = 0x49

# AK8963 registers
AK8963_WIA = 0x00
AK8963_ST1 = 0x02
AK8963_XOUT_L = 0x03
AK8963_CNTL1 = 0x0A
AK8963_ASAX = 0x10

bus = smbus2.SMBus(1)


def mpu9250_init():
    """Wake up MPU9250 and enable I2C master mode."""
    bus.write_byte_data(MPU9250_ADDR, PWR_MGMT_1, 0x00)
    time.sleep(0.1)
    bus.write_byte_data(MPU9250_ADDR, USER_CTRL, 0x20)  # I2C master enable
    time.sleep(0.1)
    bus.write_byte_data(MPU9250_ADDR, I2C_MST_CTRL, 0x0D)  # I2C master clock 400 kHz
    time.sleep(0.1)


def write_ak8963_register(reg, value):
    """Write to AK8963 register via MPU9250 I2C master."""
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_ADDR, AK8963_ADDR)  # write mode
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_REG, reg)
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_DO, value)
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_CTRL, 0x81)  # enable, 1 byte
    time.sleep(0.01)


def read_ak8963_register(reg, length=1):
    """Read AK8963 registers via MPU9250 I2C master."""
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_ADDR, AK8963_ADDR | 0x80)  # read mode
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_REG, reg)
    bus.write_byte_data(MPU9250_ADDR, I2C_SLV0_CTRL, 0x80 | length)  # enable, length bytes
    time.sleep(0.01)
    return [bus.read_byte_data(MPU9250_ADDR, EXT_SENS_DATA_00 + i) for i in range(length)]


def ak8963_init():
    """Initialize AK8963: fuse ROM for calibration, then continuous measurement."""
    # Power down
    write_ak8963_register(AK8963_CNTL1, 0x00)
    time.sleep(0.01)
    
    # Enter Fuse ROM mode to read sensitivity adjustment
    write_ak8963_register(AK8963_CNTL1, 0x0F)
    time.sleep(0.01)
    asa = read_ak8963_register(AK8963_ASAX, 3)
    sens_adj = [(x - 128) / 256 + 1 for x in asa]  # scaling factors for X, Y, Z

    # Power down again
    write_ak8963_register(AK8963_CNTL1, 0x00)
    time.sleep(0.01)

    # Continuous measurement mode 2, 16-bit output
    write_ak8963_register(AK8963_CNTL1, 0x16)
    time.sleep(0.01)

    return sens_adj


def read_mag(sens_adj):
    """Read magnetometer X, Y, Z using MPU9250 I2C master."""
    # Wait for data ready
    for _ in range(10):
        st1 = read_ak8963_register(AK8963_ST1)[0]
        if st1 & 0x01:
            break
        time.sleep(0.01)

    # Read 7 bytes: X_L, X_H, Y_L, Y_H, Z_L, Z_H, ST2
    data = read_ak8963_register(AK8963_XOUT_L, 7)

    x = (data[1] << 8) | data[0]
    y = (data[3] << 8) | data[2]
    z = (data[5] << 8) | data[4]

    # Signed conversion
    x = x - 0x10000 if x >= 0x8000 else x
    y = y - 0x10000 if y >= 0x8000 else y
    z = z - 0x10000 if z >= 0x8000 else z

    # Apply factory sensitivity adjustment
    x = x * sens_adj[0]
    y = y * sens_adj[1]
    z = z * sens_adj[2]

    return x, y, z


if __name__ == "__main__":
    mpu9250_init()
    sens_adj = ak8963_init()
    time.sleep(0.1)

    x, y, z = read_mag(sens_adj)
    print("Magnetometer (raw with factory sensitivity):", x, y, z)
