#!/usr/bin/env python2

#
# See the LICENSE file
#

import argparse
import binascii
from datetime import datetime
import struct
import sys

from google.protobuf.text_format import MessageToString, Merge

from stratatools import cartridge_pb2
from stratatools import checksum
from stratatools import crypto
from stratatools import machine
from stratatools import manager
from stratatools import material
from stratatools.formatter import DiagnosticPort_Formatter
from stratatools.setupcode import *

class StratatoolsConsoleApp():
    def __init__(self):
        self.argparse = self.build_argparser()
        self.diag_formatter = DiagnosticPort_Formatter()

    def run(self):
        args = self.argparse.parse_args()
        args.func(args)

    def parse_date(self, datestr):
        return datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")

    def build_argparser(self):
        parser = argparse.ArgumentParser(description="Stratasys EEPROM manager")

        subparsers = parser.add_subparsers(dest="command", help="Sub-commands help")

        # EEPROM encode options
        eeprom_encode = subparsers.add_parser("eeprom_encode", help="EEPROM - encode from a protobuf")
        eeprom_encode.add_argument("-t", "--machine-type", action="store", choices=machine.get_machine_types(), help="Machine type (Fox T-class, Prodigy P-class, Quantum, uPrint, uPrint SE)", required=True)
        eeprom_encode.add_argument("-e", "--eeprom-uid", action="store", dest="eeprom_uid", required=True, help="Format: [a-f0-9]{14}23, example: 11010a01ba325d23")
        eeprom_encode.add_argument("-D", "--diag-format", action="store_true", dest="diag_format", help="Produce output in the ASCII format used over the printer diagnostic port")
        eeprom_encode.add_argument("-a", "--use-ascii", action="store_true", dest="use_ascii", help="Use ASCII format for output file")
        eeprom_encode.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
        eeprom_encode.add_argument('output_file', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
        eeprom_encode.set_defaults(func=self.command_eeprom_encode)

        # EEPROM decode options
        eeprom_decode = subparsers.add_parser("eeprom_decode", help="EEPROM - decode from a binary dump")
        eeprom_decode.add_argument("-t", "--machine-type", action="store", choices=machine.get_machine_types(), help="Machine type (Fox T-class, Prodigy P-class, Quantum, uPrint, uPrint SE)", required=True)
        eeprom_decode.add_argument("-e", "--eeprom-uid", action="store", dest="eeprom_uid", required=True, help="Format: [a-f0-9]{14}23, example: 11010a01ba325d23")
        eeprom_decode.add_argument("-D", "--diag-format", action="store_true", dest="diag_format", help="Read input in the ASCII format used over the printer diagnostic port")
        eeprom_decode.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
        eeprom_decode.add_argument('output_file', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
        eeprom_decode.set_defaults(func=self.command_eeprom_decode)

        # EEPROM create options
        eeprom_create = subparsers.add_parser("eeprom_create", help="EEPROM - create a cartridge")
        eeprom_create.add_argument("-m", "--material-name", action="store", type=str, dest="material_name", help="Run \"stratatools-cli.py material --list\" for a list of known material")
        eeprom_create.add_argument("-l", "--manufacturing-lot", action="store", type=str, dest="manufacturing_lot", help="Format [0-9]{4}, examples: 1234 - 0000 - 9999")
        eeprom_create.add_argument("-d", "--manufacturing-date", action="store", type=self.parse_date, dest="manufacturing_date", help="Format \"yyyy-mm-dd hh:mm:ss\", examples: \"2014-01-01 13:14:15\"")
        eeprom_create.add_argument("-u", "--use-date", action="store", type=self.parse_date, dest="use_date", help="Format \"yyyy-mm-dd hh:mm:ss\", examples: \"2014-01-01 13:14:15\"")
        eeprom_create.add_argument("-n", "--initial-material", action="store", type=float, dest="initial_material_quantity", help="Unit: cubic inches, format [0-9]{1,}.[0-9]{1,}, examples: 91.5 - 100.0 - 0.123456789")
        eeprom_create.add_argument("-c", "--current-material", action="store", type=float, dest="current_material_quantity", help="Unit: cubic inches, format [0-9]{1,}.[0-9]{1,} examples: 91.5 - 100.0 - 0.123456789")
        eeprom_create.add_argument("-k", "--key-fragment", action="store", dest="key_fragment", help="Format [a-f0-9]{16}, examples: abcdef0123456789")
        eeprom_create.add_argument("-s", "--serial-number", action="store", type=float, dest="serial_number", help="Format: [0-9]{1,}.0, example: 1.0 - 123456789.0 - 413203.0")
        eeprom_create.add_argument("-v", "--version", action="store", type=int, dest="version", help="Format: [0-9]{1}, examples: 0 - 1")
        eeprom_create.add_argument("-g", "--signature", action="store", type=str, default="STRATASYS", dest="signature", help="Format: [a-z]{0,9}, examples: STRATASYS - MYOWNSIG - EMPTY")
        eeprom_create.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
        eeprom_create.add_argument('output_file', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
        eeprom_create.set_defaults(func=self.command_eeprom_create)

        # SetupCode create options
        setupcode_create = subparsers.add_parser("setupcode_create", help="SetupCode - create a setup code from arguments")
        setupcode_create.add_argument("-n", "--serial-number", action="store", dest="serial_number")
        setupcode_create.add_argument("-s", "--system-type", action="store", dest="system_type", choices=SystemType.all())
        setupcode_create.add_argument("-t", "--type", action="store", dest="code_type", choices=CodeType.all())
        setupcode_create.add_argument("-l", "--envelope-size", action="store", dest="envelope_size", choices=EnvelopeSize.all())
        setupcode_create.add_argument("-b", "--build-speed", action="store", dest="build_speed", choices=BuildSpeed.all())
        setupcode_create.add_argument("-m", "--material", action="store", dest="material", nargs="+", type=str, choices=CodeMaterial.all())
        setupcode_create.add_argument("-v", "--version", action="store", dest="version")
        setupcode_create.add_argument("-k", "--key", action="store", dest="key", type=int, default=0)
        setupcode_create.set_defaults(func=self.command_setupcode_create)

        # SetupCode decode options
        setupcode_decode = subparsers.add_parser("setupcode_decode", help="SetupCode - print information about a setup code")
        setupcode_decode.add_argument("setup_code", action="store")
        setupcode_decode.set_defaults(func=self.command_setupcode_decode)


        #
        # Material options
        #
        material_parser = subparsers.add_parser("material", help="Material supported by stratasys")
        material_parser.add_argument("-l", "--list", action="store_true", help="Print supported materials")
        material_parser.set_defaults(func=self.command_material)

        return parser

    def command_eeprom_encode(self, args):
        cartridge = cartridge_pb2.Cartridge()

        Merge(args.input_file.read(), cartridge)

        machine_number = machine.get_number_from_type(args.machine_type)

        m = manager.Manager(crypto.Desx_Crypto(), checksum.Crc16_Checksum())
        eeprom = m.encode(machine_number, args.eeprom_uid.decode("hex"), cartridge)

        if args.use_ascii:
            eeprom = self._make_ascii(cartridge, eeprom, args.eeprom_uid, args.machine_number)

        if args.diag_format:
            eeprom = self.diag_formatter.to_destination(eeprom)

        args.output_file.write(eeprom)

        return

    def command_eeprom_decode(self, args):
        cartridge_crypted = args.input_file.read()

        if args.diag_format:
            cartridge_crypted = self.diag_formatter.from_source(cartridge_crypted)

        m = manager.Manager(crypto.Desx_Crypto(), checksum.Crc16_Checksum())
        machine_number = machine.get_number_from_type(args.machine_type)
        cartridge = m.decode(machine_number, args.eeprom_uid.decode("hex"), bytearray(cartridge_crypted))

        args.output_file.write((MessageToString(cartridge)))

        return

    def command_eeprom_create(self, args):
        cartridge = cartridge_pb2.Cartridge()

        cartridge.serial_number = args.serial_number
        cartridge.material_name = args.material_name
        cartridge.manufacturing_lot = args.manufacturing_lot
        cartridge.manufacturing_date.FromDatetime(args.manufacturing_date)
        cartridge.last_use_date.FromDatetime(args.use_date)
        cartridge.initial_material_quantity = args.initial_material_quantity
        cartridge.current_material_quantity = args.current_material_quantity
        cartridge.key_fragment = args.key_fragment
        cartridge.version = args.version
        cartridge.signature = args.signature

        args.output_file.write((MessageToString(cartridge)))

    def command_setupcode(self, args):
        if args.setup_code:
            self._setupcode_decode(args)
        elif args.encode:
            self._setupcode_encode(args)

    def command_material(self, args):
        if args.list:
            self._material_list(args)

    def _make_ascii(self, cartridge, eeprom_bin, eeprom_uid, machine_number):
        lines = MessageToString(cartridge)

        # Prefix each line with comment `#`
        s = ""
        for l in lines:
            s += "# " + l + "\n"

        s += "# eeprom uid: " + eeprom_uid + "\n"
        s += "# machine number: " + machine_number + "\n"
        s += "#\n"

        # turn to binary into 32 chars wide ascii lines
        eeprom_ascii = binascii.b2a_hex(eeprom_bin)
        n = len(eeprom_ascii)
        for i in range(0, n, 32):
            nn = 32
            if (n - i) < 32: nn = n - i
            s += eeprom_ascii[i : i + nn] + '\n'

        return s

    def _material_list(self, args):
        for k in range(len(material.id_to_name)):
            m = material.id_to_name[k]
            if m != "unknown":
                print(str(k) + "\t" + m)

    def command_setupcode_create(self, args):
        encoder = SetupcodeEncoder()
        s = encoder.encode(args.serial_number, args.system_type, args.envelope_size, args.build_speed, args.material, args.code_type, args.version, args.key)

        print(s)

    def command_setupcode_decode(self, args):
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
        print("\tVersion:\t" + s.version)
        print("\tCode type:\t" + s.code_type)
        print("\tMaterial:\t" + s.material)
        print("\tKey:\t\t" + s.key)

def main():
    app = StratatoolsConsoleApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("quitting...")
    sys.exit(0)

if __name__ == "__main__":
    main()
