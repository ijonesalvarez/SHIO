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

class Accel_Readings:
     def __init__(self):
          imu.read_accel()
          self.ax = imu.ax
          self.ay = imu.ay
          self.az = imu.az
          self.R = math.sqrt(math.pow(self.ax, 2) + math.pow(self.ay, 2) + math.pow(self.az, 2))

class Accel_Readings_Norm:
     def __init__(self, accel):
          self.axn = accel.ax/accel.R
          self.ayn = accel.ay/accel.R
          self.azn = accel.az/accel.R

class Accel_Angles:
     def __init__(self, accel):
          self.axr = (math.acos(accel.ax/accel.R)*180)/math.pi
          self.ayr = (math.acos(accel.ay/accel.R)*180)/math.pi
          self.azr = (math.acos(accel.az/accel.R)*180)/math.pi

class Gyro_Readings:
     def __init(self):
         imu.read_gyro()
         self.gyz = imu.gx
         self.gxz = imu.gy
         self.gxy = imu.gz


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
                    while True:
                        accel = Accel_Readings()
                        accel_angles = Accel_Angles(accel)
                        tiltx = 90 - accel_angles.axr
                        tiltz = 180 - accel_angles.azr
                        if til > 0:
                            tilt = (tiltz + tiltx)/2
                        else:
                            tilt = (tiltz - tiltx)/2 
                        string = json.dumps({"An_x": accel_angles.axr, "An_y": accel_angles.ayr, "An_z": accel_angles.azr, "Tilt": tilt})	
			server_sock.send(string+"\n")
			time.sleep(0.01)
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

