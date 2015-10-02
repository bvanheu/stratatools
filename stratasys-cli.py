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
        # EEPROM options
        #
        eeprom_parser = subparsers.add_parser("eeprom", help="Create/parse a cartridge EEPROM")
        # Options used for both reading / writing eeprom
        eeprom_parser.add_argument("-t", "--machine-type", action="store", choices=["fox", "fox2", "prodigy", "quantum", "uprint", "uprintse"], help="Machine type (Fox T-class, Prodigy P-class, Quantum, uPrint, uPrint SE)", required=True)
        eeprom_parser.add_argument("-e", "--eeprom-uid", action="store", dest="eeprom_uid", required=True, help="Format: [a-f0-9]{14}23, example: 11010a01ba325d23")

        # Input or output options
        io_group = eeprom_parser.add_mutually_exclusive_group(required=True)

        # Options for EEPROM dump
        io_group.add_argument("-i", "--input-file", action="store", dest="input_file")
        input_group = eeprom_parser.add_argument_group(title="Input options", description="Option for parsing eeprom")
        input_group.add_argument("-r", "--recreate-input-file", action="store_true", help="Print information on how to recreate the cartridge")

        # Options for EEPROM creation
        io_group.add_argument("-o", "--output-file", action="store", type=str, dest="output_file")
        output_group = eeprom_parser.add_argument_group(title="Output options", description="Option for eeprom creation")
        output_group.add_argument("-m", "--material-name", action="store", type=str, dest="material_name", help="Run \"stratasys-cli.py material --list\" for a list of known material")
        output_group.add_argument("-l", "--manufacturing-lot", action="store", type=str, dest="manufacturing_lot", help="Format [0-9]{4}, examples: 1234 - 0000 - 9999")
        output_group.add_argument("-d", "--manufacturing-date", action="store", type=self.parse_date, dest="manufacturing_date", help="Format \"yyyy-mm-dd hh:mm:ss\", examples: \"2014-01-01 13:14:15\"")
        output_group.add_argument("-u", "--use-date", action="store", type=self.parse_date, dest="use_date", help="Format \"yyyy-mm-dd hh:mm:ss\", examples: \"2014-01-01 13:14:15\"")
        output_group.add_argument("-n", "--initial-material", action="store", type=float, dest="initial_material_quantity", help="Unit: cubic inches, format [0-9]{1,}.[0-9]{1,}, examples: 91.5 - 100.0 - 0.123456789")
        output_group.add_argument("-c", "--current-material", action="store", type=float, dest="current_material_quantity", help="Unit: cubic inches, format [0-9]{1,}.[0-9]{1,} examples: 91.5 - 100.0 - 0.123456789")
        output_group.add_argument("-k", "--key-fragment", action="store", dest="key_fragment", help="Format [a-f0-9]{16}, examples: abcdef0123456789")
        output_group.add_argument("-s", "--serial-number", action="store", type=float, dest="serial_number", help="Format: [0-9]{1,}.0, example: 1.0 - 123456789.0 - 413203.0")
        output_group.add_argument("-v", "--version", action="store", type=int, dest="version", help="Format: [0-9]{1}, examples: 0 - 1")
        output_group.add_argument("-g", "--signature", action="store", type=str, default="STRATASYS", dest="signature", help="Format: [a-z]{0,9}, examples: STRATASYS - MYOWNSIG - EMPTY")

        eeprom_parser.set_defaults(func=self.command_eeprom)

        #
        # Setup-codes options
        #
        setupcode_parser = subparsers.add_parser("setupcode", help="Create/parse a Stratasys setup code")
        sc_group = setupcode_parser.add_mutually_exclusive_group(required=True)
        sc_group.add_argument("-d", "--decode", action="store", dest="setup_code", help="Decode a provided code")
        sc_group.add_argument("-e", "--encode", action="store_true", dest="encode", help="")

        sc_encode = setupcode_parser.add_argument_group(title="Encode options", description="Options for setup code encoding")
        sc_encode.add_argument("-n", "--serial-number", action="store", dest="serial_number")
        sc_encode.add_argument("-s", "--system-type", action="store", dest="system_type", choices=SystemType.all())
        sc_encode.add_argument("-t", "--type", action="store", dest="code_type", choices=CodeType.all())
        sc_encode.add_argument("-l", "--envelope-size", action="store", dest="envelope_size", choices=EnvelopeSize.all())
        sc_encode.add_argument("-b", "--build-speed", action="store", dest="build_speed", choices=BuildSpeed.all())
        sc_encode.add_argument("-m", "--material", action="store", dest="material")
        sc_encode.add_argument("-v", "--version", action="store", dest="version")
        sc_encode.add_argument("-a", "--abs", action="store", dest="m_abs", type=int, default=0)
        sc_encode.add_argument("-f", "--ppsf", action="store", dest="m_ppsf", type=int, default=0)
        sc_encode.add_argument("-i", "--iso", action="store", dest="m_iso", type=int, default=0)
        sc_encode.add_argument("-k", "--key", action="store", dest="key", type=int, default=0)

        setupcode_parser.set_defaults(func=self.command_setupcode)

        #
        # Material options
        #
        material_parser = subparsers.add_parser("material", help="Material supported by stratasys")
        material_parser.add_argument("-l", "--list", action="store_true", help="Print supported materials")
        material_parser.set_defaults(func=self.command_material)

        return parser

    def command_eeprom(self, args):
        if args.input_file:
            self._eeprom_info(args)
        elif args.output_file:
            self._eeprom_create(args)

    def command_setupcode(self, args):
        if args.setup_code:
            self._setupcode_decode(args)
        elif args.encode:
            self._setupcode_encode(args)

    def command_material(self, args):
        if args.list:
            self._material_list(args)

    def _eeprom_create(self, args):
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

    def _eeprom_info(self, args):
        f = open(args.input_file, "rb")
        cartridge_crypted = bytearray(f.read())
        f.close()

        m = manager.Manager(crypto.Desx_Crypto(), checksum.Crc16_Checksum())
        machine_number = machine.get_number_from_type(args.machine_type)
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
                    + " --eeprom-uid " + str(args.eeprom_uid) \
                    + " --serial-number " + str(cartridge.serial_number) \
                    + " --material-name " + str(cartridge.material_name) \
                    + " --manufacturing-lot " + str(cartridge.manufacturing_lot) \
                    + " --manufacturing-date \"" + str(cartridge.manufacturing_date) + "\"" \
                    + " --use-date \"" + str(cartridge.use_date) + "\"" \
                    + " --initial-material " + str(cartridge.initial_material_quantity) \
                    + " --current-material " + str(cartridge.current_material_quantity) \
                    + " --key-fragment " + str(cartridge.key_fragment) \
                    + " --version " + str(cartridge.version) \
                    + " --signature " + str(cartridge.signature))

    def _material_list(self, args):
        for k in range(len(material.id_to_name)):
            m = material.id_to_name[k]
            if m != "unknown":
                print(str(k) + "\t" + m)

    def _setupcode_encode(self, args):
        encoder = SetupcodeEncoder()
        encoder.encode(args.serial_number, args.system_type, args.envelope_size, args.build_speed, args.material, args.code_type, args.version, args.m_abs, args.m_ppsf, args.m_iso, args.key)

    def _setupcode_decode(self, args):
        encoder = SetupcodeEncoder()
        s = encoder.decode(args.setup_code)

        print("Setup code")
        print("\tChecksum 1:\t" + s.checksum_1)
        print("\tChecksum 2:\t" + s.checksum_2)
        print("\t-------------------------------")
        print("\tSerial number:\t" + s.serial_number)
        print("\tSystem type:\t" + s.system_type)
        print("\tEnvelope size:\t" + s.envelope_size)
        print("\tBuild speed:\t" + s.build_speed)
        print("\tABS:\t\t" + s.mat_abs)
        print("\tPPSF:\t\t" + s.mat_ppsf)
        print("\tISO:\t\t" + s.mat_iso)
        print("\tVersion:\t" + s.version)
        print("\tCode type:\t" + s.code_type)
        print("\tMaterial:\t" + s.material)
        print("\tKey:\t\t" + s.key)

if __name__ == "__main__":
    app = StratasysConsoleApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("quitting...")
    sys.exit(0)
