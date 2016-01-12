#!/bin/sh

/usr/sbin/rfkill unblock bluetooth
/usr/bin/hciconfig hci0 up
/usr/bin/hciconfig hci0 piscan

/usr/bin/python 9dofBlock-master/SPP-loopback.py
