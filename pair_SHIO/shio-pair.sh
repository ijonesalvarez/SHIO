#!/bin/sh

/usr/sbin/rfkill unblock bluetooth

/usr/bin/hciconfig hci0 up
sleep 5
/usr/bin/hciconfig hci0 piscan &

sleep 5 

/home/root/pair_SHIO/simple-agent1 &
python /home/root/pair_SHIO/SPP-loopback.py &
