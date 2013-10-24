#!/usr/bin/env python2

# Copyright (c) 2013, Benjamin Vanheuverzwijn <bvanheu@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <BENJAMIN VANHEUVERZWIJN> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import struct
import sys
from datetime import datetime
from datetime import datetime

from stratasys.cartridge import Cartridge
from stratasys.material import Material
from stratasys.manager import Manager
from stratasys.crypto import Desx_Crypto
from stratasys.checksum import Crc16_Checksum

class StratasysConsoleApp():
    def __init__(self):
        self.argparse = self.build_argparser()

    def run(self):
        args = self.argparse.parse_args()
        args.func(args)

    def parse_date(self, datestr):
        return datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")

    def parse_hexadecimal(self, data):
        return bytearray(data.decode("hex"))

    def build_argparser(self):
        parser = argparse.ArgumentParser(description="Stratasys EEPROM manager")

        subparsers = parser.add_subparsers(dest="command", help="Sub-commands help")

        # create (a eeprom that you can burn on your cartridge)
        parser_create = subparsers.add_parser("create", help="Create an EEPROM that you can flash on your cartridge")
        parser_create.add_argument("-f", "--format", action="store", type=str, dest="format", help="Output format")
        parser_create.add_argument("-t", "--machine-type", action="store", choices=["fox", "prodigy", "quantum"], help="Machine type (Fox T-class, Prodigy P-class, Quantum)")
        parser_create.add_argument("-e", "--eeprom-uid", action="store", type=self.parse_hexadecimal, dest="eeprom_uid", help="EEPROM uid (hex form)")

        parser_create.add_argument("-m", "--material-name", action="store", type=str, dest="material_name")
        parser_create.add_argument("-l", "--manufacturing-lot", action="store", type=str, dest="manufacturing_lot")
        parser_create.add_argument("-d", "--manufacturing-date", action="store", type=self.parse_date, dest="manufacturing_date")
        parser_create.add_argument("-u", "--use-date", action="store", type=self.parse_date, dest="use_date")
        parser_create.add_argument("-i", "--initial-material", action="store", type=float, dest="initial_material_quantity")
        parser_create.add_argument("-c", "--current-material", action="store", type=float, dest="current_material_quantity")
        parser_create.add_argument("-k", "--key-fragment", action="store", type=self.parse_hexadecimal, dest="key_fragment")
        parser_create.add_argument("-s", "--serial-number", action="store", type=float, dest="serial_number")
        parser_create.add_argument("-v", "--version", action="store", type=int, dest="version")
        parser_create.add_argument("-g", "--signature", action="store", type=str, dest="signature")
        parser_create.add_argument("-o", "--output", action="store", type=str, dest="output_path")
        parser_create.set_defaults(func=self.command_create)

        # info (print information about an eeprom that you dump'ed)
        parser_info = subparsers.add_parser("info", help="Print information about a EEPROM dump")

        parser_info.add_argument("-f", "--format", action="store", type=str, dest="format", help="Input format")
        parser_info.add_argument("-t", "--machine-type", action="store", choices=["fox", "prodigy", "quantum"], help="Machine type (Fox T-class, Prodigy P-class, Quantum)")
        parser_info.add_argument("-e", "--eeprom-uid", action="store", type=self.parse_hexadecimal, dest="eeprom_uid", help="EEPROM uid (hex form)")

        parser_info.add_argument("-i", "--input-path", action="store", dest="input_path", help="Input path")
        parser_info.add_argument("-u", "--human-output", action="store_true", help="Human readable format")
        parser_info.add_argument("-r", "--recreate-output", action="store_true", help="Format that facilitates the recreation of the cartridge")
        parser_info.set_defaults(func=self.command_info)

        return parser

    def command_create(self, args):
        cartridge = Cartridge(args.serial_number,
                Material.from_name(args.material_name),
                args.manufacturing_lot,
                args.manufacturing_date,
                args.use_date,
                args.initial_material_quantity,
                args.current_material_quantity,
                args.key_fragment,
                args.version,
                args.signature)

        machine_number = bytearray("0000000000000000".decode("hex"))
        if args.machine_type == "fox":
            machine_number = bytearray("2C30478BB7DE81E8".decode("hex"))
        elif args.machine_type == "prodigy":
            machine_number = bytearray("5394D7657CED641D".decode("hex"))
        elif args.machine_type == "quantum":
            machine_number = bytearray("76C454D532E610F7".decode("hex"))

        m = Manager(Desx_Crypto(), Crc16_Checksum())
        eeprom = m.encode(machine_number, args.eeprom_uid, cartridge)

        f = open(args.output_path, "wb")
        f.write(eeprom)
        f.close()

    def command_info(self, args):
        f = open(args.input_path, "rb")
        cartridge_crypted = bytearray(f.read())
        f.close()

        machine_number = bytearray("0000000000000000".decode("hex"))
        if args.machine_type == "fox":
            machine_number = bytearray("2C30478BB7DE81E8".decode("hex"))
        elif args.machine_type == "prodigy":
            machine_number = bytearray("5394D7657CED641D".decode("hex"))
        elif args.machine_type == "quantum":
            machine_number = bytearray("76C454D532E610F7".decode("hex"))

        m = Manager(Desx_Crypto(), Crc16_Checksum())
        cartridge = m.decode(machine_number, args.eeprom_uid, cartridge_crypted)

        if args.human_output:
            print("Cartridge")
            print("---------")
            print("Serial number\t\t" + str(cartridge.serial_number))
            print("Material\t\t" + cartridge.material.name + " (" + str(cartridge.material.id) + " - " + hex(cartridge.material.id) +")")
            print("Manufacturing lot\t" + str(cartridge.manufacturing_lot))
            print("Manufacturing date\t" + str(cartridge.manufacturing_date))
            print("Last use date\t\t" + str(cartridge.use_date))
            print("Initial quantity\t" + str(cartridge.initial_material_quantity))
            print("Current quantity\t" + str(cartridge.current_material_quantity))
            print("Key fragment\t\t" + str(cartridge.key_fragment).encode("hex"))
            print("Version\t\t\t" + str(cartridge.version))
            print("Signature\t\t" + str(cartridge.signature))
            print("---------")

        if args.recreate_output:
            print("To recreate the provided cartridge:")
            print("--machine-type " + str(args.machine_type) \
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

if __name__ == "__main__":
    app = StratasysConsoleApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("quitting...")
    sys.exit(0)
