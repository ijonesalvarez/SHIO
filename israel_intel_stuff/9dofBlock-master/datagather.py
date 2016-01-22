from SF_9DOF import IMU
import time
import numpy as np

# Create IMU object
imu = IMU() # To select a specific I2C port, use IMU(n). Default is 1. 

# Initialize IMU
imu.initialize()

# Enable accel, mag, gyro, and temperature
imu.enable_accel()
imu.enable_mag()
imu.enable_gyro()
imu.enable_temp()

# Set range on accel, mag, and gyro

# Specify Options: "2G", "4G", "6G", "8G", "16G"
imu.accel_range("2G")       # leave blank for default of "2G" 

# Specify Options: "2GAUSS", "4GAUSS", "8GAUSS", "12GAUSS"
imu.mag_range("2GAUSS")     # leave blank for default of "2GAUSS"

# Specify Options: "245DPS", "500DPS", "2000DPS" 
imu.gyro_range("245DPS")    # leave blank for default of "245DPS"

# Loop and read accel, mag, and gyro

class Offset_Gyro:
    def __init__(self):
         imu.read_gyro()
         self.gx = imu.gx
         self.gy = imu.gy
         self.gz = imu.gz

gyro_offset = Offset_Gyro()

def gyro_offset_calc():
    print "Calculating Gyroscope Offsets..."
    for i in range(2, 102):
            new_gyro_data = Offset_Gyro()
            gyro_offset.gx = ((i-1)/i)*gyro_offset.gx + new_gyro_data.gx/i
            gyro_offset.gy = ((i-1)/i)*gyro_offset.gy + new_gyro_data.gy/i
            gyro_offset.gz = ((i-1)/i)*gyro_offset.gz + new_gyro_data.gz/i
            time.sleep(0.1)

gyro_offset_calc()

class Offset_Accel:
    def __init__(self):
        imu.read_accel()
        self.ax = imu.ax
        self.ay = imu.ay
        self.az = imu.az

accel_offset = Offset_Accel()

def accel_offset_calc():
    print "Calculating Accelerometer Offsets..."
    for i in range(2, 102):
        new_accel_data = Offset_Accel()
        accel_offset.ax = ((i-1)/i)*accel_offset.ax + new_accel_data.ax/i
        accel_offset.ay = ((i-1)/i)*accel_offset.ay + new_accel_data.ay/i
        accel_offset.az = ((i-1)/i)*accel_offset.az + new_accel_data.az/i
        time.sleep(0.1)

accel_offset_calc()

accel_x = [0, 0, 0]
accel_time = [0, 0, 0]

for i in range(1,3):
    imu.read_accel()
    current_time = time.time()
    accel_x.pop(0)
    accel_x.append(imu.ax-accel_offset.ax)
    accel_time.pop(0)
    accel_time.append(current_time)

velocity = 0

while(1):
    imu.read_accel()
    current_time = time.time()
    imu.read_mag()
    imu.read_gyro()
    imu.readTemp()

    accel_x.pop(0)
    accel_x.append(imu.ax-accel_offset.ax)
    accel_time.pop(0)
    accel_time.append(current_time)

    velocity = np.trapz([accel_x[0], accel_x[2]], x=[0, accel_time[2]-accel_time[0]]) 

    with open('gyrodata.txt', 'a') as f:
        f.write(imu.gx-gyro_offset.gx)
    f.closed

    # Print the results
    #print "Accel: " + str(imu.ax-accel_offset.ax) + ", " + str(imu.ay-accel_offset.ay) + ", " + str(imu.az-accel_offset.az) 
    #print "Mag: " + str(imu.mx) + ", " + str(imu.my) + ", " + str(imu.mz) 
    #print "Gyro: " + str(imu.gx-gyro_offset.gx) + ", " + str(imu.gy-gyro_offset.gy) + ", " + str(imu.gz-gyro_offset.gz) 
    #print "Temperature: " + str(imu.temp) 

    # Sleep for 1/10th of a second
    time.sleep(0.1)
