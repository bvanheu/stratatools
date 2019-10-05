#!/usr/bin/env python2

import argparse
import binascii
import pyudev
import sys
import time
import traceback

from stratatools import *
from stratatools import machine,cartridge,manager,crypto,checksum,cartridge_pb2
from google.protobuf.text_format import MessageToString, Merge

cartridge_manager = None
machine_number = None
cartridge_template = None

def read_bytes(path):
    data = None
    with open(path, "r") as f:
        data = bytearray(f.read())
    return data

def write_bytes(path, data):
    with open(path, "w", buffering=0) as f:
        f.write(data)

def on_new_cartridge(device):
    eeprom_path = "/sys/" + device.device_path + "/eeprom"
    eeprom_uid = read_bytes("/sys/" + device.device_path + "/id")

    print("New device detected <" + binascii.hexlify(eeprom_uid) + ">.")
    try:
        c = cartridge_template

        if c is None:
            c = cartridge_manager.decode(machine_number, eeprom_uid, read_bytes(eeprom_path))
            print("Device is a valid cartridge.")

        c = cartridge.refill(c)

        write_bytes(eeprom_path, cartridge_manager.encode(machine_number, eeprom_uid, c))

        print("Refill complete!")
        print("You can safely disconnect the cartridge.")
    except Exception as e:
        print("Error! verify machine type?")
        print("Details:")
        traceback.print_exc()

def read_cartridge_template(path):
    catridge = None

    with open(path, "r") as f:
        cartridge = cartridge_pb2.Cartridge()
        Merge(f.read(), cartridge)

    return cartridge

def main():
    global cartridge_manager
    global machine_number
    global cartridge_template

    parser = argparse.ArgumentParser(description="Raspberry Pi Flasher Daemon")
    parser.add_argument("-t", "--template", action="store", type=str,  dest="template", help="Path to cartridge configuration")
    parser.add_argument("machine_type", action="store", choices=machine.get_machine_types())
    args = parser.parse_args()

    cartridge_manager = manager.Manager(crypto.Desx_Crypto(), checksum.Crc16_Checksum())
    machine_number = machine.get_number_from_type(args.machine_type)
    cartridge_template = None

    if args.template:
        cartridge_template = read_cartridge_template(args.template)
        print("Fill cartridge using template from <" + args.template + ">.")

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('w1')

    observer = pyudev.MonitorObserver(monitor, callback=on_new_cartridge)
    observer.start()

    try:
        print("Listening to new device ... ^c to quit")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    observer.stop()

if __name__ == "__main__":
    main()

