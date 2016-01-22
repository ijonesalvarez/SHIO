SHIO

Steps to allow edison to connect to a device automatically

cp pair_SHIO /home/root/
cd pair_SHIO/9dofmaster... and run ./dependencies.sh
cd ..
mv bluetooth-pair.service /lib/systemd/system/bluetooth-pair.service
systemctl enable bluetooth-pair
reboot
