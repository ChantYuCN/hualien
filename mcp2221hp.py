#!/usr/bin/python3
import subprocess
import os
import sys
import argparse
import xml.etree.ElementTree as ET
import re

tpcvm = "nucvm"

def attachUsb():
    clbl='\b\n'
    cmdattach =  ["virsh", "attach-device", tpcvm, "/dev/stdin"]
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.run(['lsusb'], capture_output=True, text=True)
    devices = []   
    for i in df.stdout.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                #dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                y = dinfo.pop('id').split(':')
                dinfo['vid'] = "0x"+y[0]
                dinfo['did'] = "0x"+y[1]
                dinfo['bus'] = dinfo.pop('bus').strip('0')
                dinfo['device'] = dinfo.pop('device').strip('0')
                devices.append(dinfo)
    #print(devices)
    hostdev_xml = '<hostdev mode="subsystem" type="usb" managed="yes"><source><vendor id="{}"/><product id="{}"/><address bus="{}" device="{}"/></source><alias name="{}"/></hostdev>'
    for dev in devices:
        #print(dev)
        x = ""
        if "MCP0_0" in dev.get("tag"):
            print("MCP1_0 found")
            virshattach = subprocess.Popen(
                cmdattach,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
            )
            x = hostdev_xml.format(dev.get("vid"),dev.get("did"),dev.get("bus"), dev.get("device"),"hosdev0")
            virshattach.communicate(input=x.encode("ASCII")) 
            result = virshattach.wait()
            if result != 0:
                print(f"virsh failed to attach device")
        if "MCP1_0" in dev.get("tag"):
            print("MCP0_0 found")
            virshattach = subprocess.Popen(
                cmdattach,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
            )
            x = hostdev_xml.format(dev.get("vid"),dev.get("did"),dev.get("bus"), dev.get("device"),"hosdev2")
            virshattach.communicate(input=x.encode("ASCII"))
            result = virshattach.wait()
            if result != 0:
                print(f"virsh failed to attach device")
        if "FT2232C" in dev.get("tag"):
            print("FT2232C found")
            virshattach = subprocess.Popen(
                cmdattach,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
            )
            x = hostdev_xml.format(dev.get("vid"),dev.get("did"),dev.get("bus"), dev.get("device"),"hosdev1")
            virshattach.communicate(input=x.encode("ASCII"))
            result = virshattach.wait()
            if result != 0:
                print(f"virsh failed to attach device")

    #hostdev_xml = '<hostdev mode="subsystem" type="usb"><source><address bus="{}" device="{}"/></source></hostdev>'
    #device_xml = device_xml.format(mount.busnum, mount.devnum)
    print("attach mcp2221 successfully or deivce is already attached")


def detachUsb():
    command = ["virsh", "dumpxml", tpcvm]
    cmddetach = ["virsh", "detach-device", tpcvm, "/dev/stdin"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        xml_output = result.stdout
        #tree = ET.parse(xml_output)
        #root = tree.getroot() # Get the root element
        root = ET.fromstring(xml_output)
    except subprocess.CalledProcessError as e:
        print(f"Failed to dump xml from: {e}")
    devs = root.find('devices')

    for ax in devs:
        if ax.tag == 'hostdev':
            print("found")
    #childs = devs.find('hostdev')
            childs = ax
            if childs:
                x = ""
                pre = "<hostdev mode='subsystem' type='usb' managed='yes'> "
                post = "</hostdev>"
                x = x + pre
                for chill in childs:
                    x = x + str(ET.tostring(chill))
                x = x + post
                x = x.replace(">b","")
                x = x.replace("\\n","")
                x = x.replace("'b'","")
                x = x.strip()
                print(x)
                virshdetach = subprocess.Popen(
                    cmddetach,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                )
    # input the variable directly
                virshdetach.communicate(input=x.encode('ASCII'))
                result = virshdetach.wait()
                if result != 0:
                    print(f"virtsh failed for device code: {result}")


            else:
                print(f"No hostdev elements found.")
                return
    print("detach mcp2221 successfully")


def main():
    parser = argparse.ArgumentParser(description='Attach or Detach MCP2221 to TPC VM')
    parser.add_argument("-m", "--mode", choices=["attach", "detach"])   
    parser.add_argument("-d", "--domain", type=str)
    args = parser.parse_args()
    if args.domain is not None:
        tpcvm = args.domain
        print("Domain targe is: ", tpcvm)

    if args.mode == "detach":
        detachUsb()
    elif args.mode == "attach": 
        attachUsb()


if __name__ == "__main__":
    main()
