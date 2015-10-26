#!/usr/bin/env python2

#
# See the LICENSE file
#

import argparse
import struct
import sys
from datetime import datetime

from stratasys import cartridge
from stratasys import material
from stratasys import machine
from stratasys import manager
from stratasys import crypto
from stratasys import checksum
from stratasys.setupcode import *

class StratasysConsoleApp():
    def __init__(self):
        self.argparse = self.build_argparser()

    def run(self):
        args = self.argparse.parse_args()
        args.func(args)

    def parse_date(self, datestr):
        return datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")

    def build_argparser(self):
        parser = argparse.ArgumentParser(description="Stratasys EEPROM manager")

        subparsers = parser.add_subparsers(dest="command", help="Sub-commands help")

        #
        # Create a cartridge
        #
        create_parser = subparsers.add_parser("create", help="Create a cartridge")
        create_parser.add_argument("-t", "--machine-type", action="store", choices=["fox", "fox2", "prodigy", "quantum", "uprint", "uprintse"], help="Machine type (Fox T-class, Prodigy P-class, Quantum, uPrint, uPrint SE)", required=True)
        create_parser.add_argument("-e", "--eeprom-uid", action="store", dest="eeprom_uid", required=True, help="Format: [a-f0-9]{14}23, example: 11010a01ba325d23")
        create_parser.add_argument("-o", "--output-file", action="store", type=str, dest="output_file")
        create_parser.add_argument("-m", "--material-name", action="store", type=str, dest="material_name", help="Run \"stratasys-cli.py material --list\" for a list of known material")
        create_parser.add_argument("-l", "--manufacturing-lot", action="store", type=str, dest="manufacturing_lot", help="Format [0-9]{4}, examples: 1234 - 0000 - 9999")
        create_parser.add_argument("-d", "--manufacturing-date", action="store", type=self.parse_date, dest="manufacturing_date", help="Format \"yyyy-mm-dd hh:mm:ss\", examples: \"2014-01-01 13:14:15\"")
        create_parser.add_argument("-u", "--use-date", action="store", type=self.parse_date, dest="use_date", help="Format \"yyyy-mm-dd hh:mm:ss\", examples: \"2014-01-01 13:14:15\"")
        create_parser.add_argument("-n", "--initial-material", action="store", type=float, dest="initial_material_quantity", help="Unit: cubic inches, format [0-9]{1,}.[0-9]{1,}, examples: 91.5 - 100.0 - 0.123456789")
        create_parser.add_argument("-c", "--current-material", action="store", type=float, dest="current_material_quantity", help="Unit: cubic inches, format [0-9]{1,}.[0-9]{1,} examples: 91.5 - 100.0 - 0.123456789")
        create_parser.add_argument("-k", "--key-fragment", action="store", dest="key_fragment", help="Format [a-f0-9]{16}, examples: abcdef0123456789")
        create_parser.add_argument("-s", "--serial-number", action="store", type=float, dest="serial_number", help="Format: [0-9]{1,}.0, example: 1.0 - 123456789.0 - 413203.0")
        create_parser.add_argument("-v", "--version", action="store", type=int, dest="version", help="Format: [0-9]{1}, examples: 0 - 1")
        create_parser.add_argument("-g", "--signature", action="store", type=str, default="STRATASYS", dest="signature", help="Format: [a-z]{0,9}, examples: STRATASYS - MYOWNSIG - EMPTY")

        create_parser.set_defaults(func=self.command_create)

        #
        # Information about a cartridge
        #
        info_parser = subparsers.add_parser("info", help="Print information about a cartridge")
        info_parser.add_argument("-t", "--machine-type", action="store", choices=["fox", "fox2", "prodigy", "quantum"], help="Machine type (Fox T-class, Prodigy P-class, Quantum)", required=True)
        info_parser.add_argument("-e", "--eeprom-uid", action="store", dest="eeprom_uid", help="Format: [a-f0-9]{14}23, example: 11010a01ba325d23", required=True)
        info_parser.add_argument("-i", "--input-file", action="store", dest="input_file", required=True)
        info_parser.add_argument("-r", "--recreate-input-file", action="store_true", help="Print information on how to recreate the cartridge")
        info_parser.set_defaults(func=self.command_info)

        #
        # Refill an existing cartridge
        #
        refill_parser = subparsers.add_parser("refill", help="Print information about a cartridge")
        # Mandatory option
        refill_parser.add_argument("-t", "--machine-type", action="store", choices=["fox", "fox2", "prodigy", "quantum"], help="Machine type (Fox T-class, Prodigy P-class, Quantum)", required=True)
        refill_parser.add_argument("-e", "--eeprom-uid", action="store", dest="eeprom_uid", help="Format: [a-f0-9]{14}23, example: 11010a01ba325d23", required=True)
        refill_parser.add_argument("-i", "--input-file", action="store", type=str, dest="input_file", required=True)
        refill_parser.add_argument("-o", "--output-file", action="store", type=str, dest="output_file", required=True)
        # Optional option
        refill_parser.add_argument("-m", "--material-name", action="store", type=str, dest="material_name", help="Run \"stratasys-cli.py material --list\" for a list of known material")
        refill_parser.add_argument("-l", "--manufacturing-lot", action="store", type=str, dest="manufacturing_lot", help="Format [0-9]{4}, examples: 1234 - 0000 - 9999")
        refill_parser.add_argument("-n", "--initial-material", action="store", type=float, dest="initial_material_quantity", help="Unit: cubic inches, format [0-9]{1,}.[0-9]{1,}, examples: 91.5 - 100.0 - 0.123456789")
        refill_parser.add_argument("-s", "--serial-number", action="store", type=float, dest="serial_number", help="Format: [0-9]{1,}.0, example: 1.0 - 123456789.0 - 413203.0")
        refill_parser.set_defaults(func=self.command_refill)

        return parser

    def command_create(self, args):
        cart = cartridge.Cartridge(args.serial_number,
                args.material_name,
                args.manufacturing_lot,
                args.manufacturing_date,
                args.use_date,
                args.initial_material_quantity,
                args.current_material_quantity,
                args.key_fragment,
                args.version,
                args.signature)

        machine_number = machine.get_number_from_type(args.machine_type)

        m = manager.Manager(crypto.Desx_Crypto(), checksum.Crc16_Checksum())
        eeprom = m.encode(machine_number, args.eeprom_uid, cart)

        f = open(args.output_file, "wb")
        f.write(eeprom)
        f.close()

    def command_info(self, args):
        f = open(args.input_file, "rb")
        cartridge_crypted = bytearray(f.read())
        f.close()

        machine_number = machine.get_number_from_type(args.machine_type)

        m = manager.Manager(crypto.Desx_Crypto(), checksum.Crc16_Checksum())
        cartridge = m.decode(machine_number, args.eeprom_uid, cartridge_crypted)

        print("Cartridge - '" + args.input_file + "'")
        print("-"*79)
        print("Serial number\t\t" + str(cartridge.serial_number))
        material_id = material.get_id_from_name(cartridge.material_name)
        print("Material\t\t" + cartridge.material_name + " (" + str(material_id) + " - " + hex(material_id) +")")
        print("Manufacturing lot\t" + str(cartridge.manufacturing_lot))
        print("Manufacturing date\t" + str(cartridge.manufacturing_date))
        print("Last use date\t\t" + str(cartridge.use_date))
        print("Initial quantity\t" + str(cartridge.initial_material_quantity))
        print("Current quantity\t" + str(cartridge.current_material_quantity))
        print("Key fragment\t\t" + str(cartridge.key_fragment))
        print("Version\t\t\t" + str(cartridge.version))
        print("Signature\t\t" + str(cartridge.signature))
        print("")
        print("Machine type:\t\t" + str(args.machine_type) + " " + str(machine_number))
        print("EEPROM uid:\t\t" + str(args.eeprom_uid))

        if args.recreate_input_file:
            print("\nTo recreate this cartridge:")
            print("--output-file XXX_REPLACE_ME_XXX " \
                    + "--machine-type " + str(args.machine_type) \
                    + " --eeprom-uid " + str(args.eeprom_uid).encode("hex") \
                    + " --serial-number " + str(cartridge.serial_number) \
                    + " --material-name " + str(cartridge.material.name) \
                    + " --manufacturing-lot " + str(cartridge.manufacturing_lot) \
                    + " --manufacturing-date \"" + str(cartridge.manufacturing_date) + "\"" \
                    + " --use-date \"" + str(cartridge.use_date) + "\"" \
                    + " --initial-material " + str(cartridge.initial_material_quantity) \
                    + " --current-material " + str(cartridge.current_material_quantity) \
                    + " --key-fragment " + str(cartridge.key_fragment).encode("hex") \
                    + " --version " + str(cartridge.version) \
                    + " --signature " + str(cartridge.signature))

    def command_refill(self, args):
        f = open(args.input_file, "rb")
        cartridge_crypted = bytearray(f.read())
        f.close()

        machine_number = machine.get_number_from_type(args.machine_type)

        m = manager.Manager(crypto.Desx_Crypto(), checksum.Crc16_Checksum())
        c = m.decode(machine_number, args.eeprom_uid, cartridge_crypted)

        material_name = c.material_name if args.material_name == None else args.material_name
        manufacturing_lot = c.manufacturing_lot if args.manufacturing_lot == None else args.manufacturing_lot
        manufacturing_date = datetime.now()
        serial_number = int(c.serial_number)+1 if args.serial_number == None else args.serial_number
        initial_material_quantity = float(c.initial_material_quantity) if args.initial_material_quantity == None else args.initial_material_quantity

        new_c = cartridge.Cartridge(serial_number,
                material_name,
                manufacturing_lot,
                manufacturing_date,
                manufacturing_date,
                initial_material_quantity,
                initial_material_quantity,
                c.key_fragment,
                c.version,
                c.signature)

        eeprom = m.encode(machine_number, args.eeprom_uid, new_c)
        f = open(args.output_file, "wb")
        f.write(eeprom)
        f.close()

if __name__ == "__main__":
    app = StratasysConsoleApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("quitting...")
    sys.exit(0)
