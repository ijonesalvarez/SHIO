from SF_9DOF import IMU
import time
import numpy as np
import math

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
# accelerometer readings are given in G's

class Accel_Readings:
    def __init__(self):
        imu.read_accel()
        self.ax = imu.ax
        self.ay = imu.ay
        self.az = imu.az
        self.R = math.sqrt(math.pow(self.ax, 2) + math.pow(self.ay, 2) + math.pow(self.az, 2))

#Returns in degrees
class Accel_Angles:
    def __init__(self, accel):
        self.axr = (math.acos(accel.ax/accel.R)*180)/math.pi
        self.ayr = (math.acos(accel.ay/accel.R)*180)/math.pi
        self.azr = (math.acos(accel.az/accel.R)*180)/math.pi


while (1):
    accel = Accel_Readings()
    print "accel readings in g"
    print "R: " + str(accel.R) + " x: " + str(accel.ax) + " y: " + str(accel.ay) + " z: " + str(accel.az)

    accel_angles = Accel_Angles(accel)
    print "accel angles in degrees"
    print "Ax: " + str(accel_angles.axr) + " Ay: " + str(accel_angles.ayr) + " Az: " + str(accel_angles.azr)
    time.sleep(1)

print "test done"
gyro_data.close()
time_data.close()
