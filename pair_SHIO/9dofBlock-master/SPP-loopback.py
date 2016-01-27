#!/usr/bin/python

from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser, make_option
import os
import sys
import time
import socket
import uuid
import dbus
import dbus.service
import dbus.mainloop.glib
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject


from SF_9DOF import IMU
import time
import json
import numpy as np

imu = IMU()

imu.initialize()
imu.enable_accel()
imu.enable_mag()
imu.enable_gyro()
imu.enable_temp()

imu.accel_range("2G")
imu.mag_range("2GAUSS")
imu.gyro_range("245DPS")

class Offset_Gyro:
    def __init__(self):
        imu.read_gyro()
        self.gx = imu.gx
        self.gy = imu.gy
        self.gz = imu.gz
gyro_offset = Offset_Gyro()

def gyro_offset_calc():
    print("Calculating Gyroscope Offset...")
    for i in range(2, 102):
        new_gyro_data = Offset_Gyro()
        gyro_offset.gx = ((i-1)/i)*gyro_offset.gx + new_gyro_data.gx/i
        gyro_offset.gy = ((i-1)/i)*gyro_offset.gy + new_gyro_data.gy/i
        gyro_offset.gz = ((i-1)/i)*gyro_offset.gz + new_gyro_data.gz/i
        time.sleep(0.1)


class Offset_Accel:
    def __init__(self):
        imu.read_accel()
        self.ax = imu.ax
        self.ay = imu.ay
        self.az = imu.az

accel_offset = Offset_Accel()

def accel_offset_calc():
    print("Calculating Acceleration Offset...")
    for i in range(2, 102):
        new_accel_data = Offset_Accel()
        accel_offset.ax = ((i-1)/i)*accel_offset.ax + new_accel_data.ax/i
        accel_offset.ay = ((i-1)/i)*accel_offset.ay + new_accel_data.ay/i
        accel_offset.az = ((i-1)/i)*accel_offset.az + new_accel_data.az/i
        time.sleep(0.1)


class Profile(dbus.service.Object):
	fd = -1

	@dbus.service.method("org.bluez.Profile1",
					in_signature="", out_signature="")
	def Release(self):
		print("Release")
		mainloop.quit()

	@dbus.service.method("org.bluez.Profile1",
					in_signature="", out_signature="")
	def Cancel(self):
		print("Cancel")

	@dbus.service.method("org.bluez.Profile1",
				in_signature="oha{sv}", out_signature="")
	def NewConnection(self, path, fd, properties):
		self.fd = fd.take()
		print("NewConnection(%s, %d)" % (path, self.fd))


		server_sock = socket.fromfd(self.fd, socket.AF_UNIX, socket.SOCK_STREAM)
		server_sock.setblocking(1)
		server_sock.send("This is Edison SPP loopback test\nAll data will be loopback\nPlease start:\n")

		try:
                    accel_x = [0,0,0]
                    accel_time = [0,0,0]
                    print("Begining Calibrations")
                    accel_offset_calc()
                    gyro_offset_calc()
                    print("Calibration Completed")
                    for i in range(1,3):
                        imu.read_accel()
                        current_time = time.time()
                        accel_x.pop(0)
                        accel_x.append(imu.ax-accel_offset.ax)
                        accel_time.pop(0)
                        accel_time.append(current_time)
                    velocity = 0

                    while True:
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
                        print('Acceleration before offset x: ' + str(imu.ax))
                        print("Acceleration x: " + str(imu.ax-accel_offset.ax))
                        print("time: " + str(accel_time[2]))
                        print("Velocity: " + str(velocity))

                        string = json.dumps({"A_x": imu.ax-accel_offset.ax, "A_y": imu.ay-accel_offset.ay, "A_z": imu.az-accel_offset.az, "V_x": velocity})	
			server_sock.send(string+"\n")
			time.sleep(1)
		except IOError:
		    pass

		server_sock.close()
		print("all done")



	@dbus.service.method("org.bluez.Profile1",
				in_signature="o", out_signature="")
	def RequestDisconnection(self, path):
		print("RequestDisconnection(%s)" % (path))

		if (self.fd > 0):
			os.close(self.fd)
			self.fd = -1

if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SystemBus()

	manager = dbus.Interface(bus.get_object("org.bluez",
				"/org/bluez"), "org.bluez.ProfileManager1")

	option_list = [
			make_option("-C", "--channel", action="store",
					type="int", dest="channel",
					default=None),
			]

	parser = OptionParser(option_list=option_list)

	(options, args) = parser.parse_args()

	options.uuid = "1101"
	options.psm = "3"
	options.role = "server"
	options.name = "Edison SPP Loopback"
	options.service = "spp char loopback"
	options.path = "/foo/bar/profile"
	options.auto_connect = False
	options.record = ""

	profile = Profile(bus, options.path)

	mainloop = GObject.MainLoop()

	opts = {
			"AutoConnect" :	options.auto_connect,
		}

	if (options.name):
		opts["Name"] = options.name

	if (options.role):
		opts["Role"] = options.role

	if (options.psm is not None):
		opts["PSM"] = dbus.UInt16(options.psm)

	if (options.channel is not None):
		opts["Channel"] = dbus.UInt16(options.channel)

	if (options.record):
		opts["ServiceRecord"] = options.record

	if (options.service):
		opts["Service"] = options.service

	if not options.uuid:
		options.uuid = str(uuid.uuid4())

	manager.RegisterProfile(options.path, options.uuid, opts)

	mainloop.run()

