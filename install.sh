#!/bin/bash

#set -u
# not allow the input name

DOM=nucvm

if [[ ! -z $DOMUSB ]];then
    DOM=$DOMUSB
fi

pip install -r requirement.txt
pyinstaller mcp2221hp.py
sudo install dist/mcp2221hp/mcp2221hp  /usr/local/bin/
echo 'SUBSYSTEM=="usb", ACTION=="add", RUN+="/usr/local/bin/mcp2221hp --mode attach --domain DOMNAME"' | sudo tee  /etc/udev/rules.d/99-tpe-standalne-mcp2221.rules
echo 'SUBSYSTEM=="usb", ACTION=="remove", RUN+="/usr/local/bin/mcp2221hp --mode detach --domain DOMNAME"' | sudo tee -a /etc/udev/rules.d/99-tpe-standalne-mcp2221.rules
sudo sed -i "s/DOMNAME/$DOM/g" /etc/udev/rules.d/99-tpe-standalne-mcp2221.rules
sudo cp -r dist/mcp2221hp/_internal /usr/local/bin/
sudo udevadm control --reload-rules
