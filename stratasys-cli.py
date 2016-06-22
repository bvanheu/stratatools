#!/usr/bin/env python2

#
# See the LICENSE file
#

import argparse
import struct
import sys
from datetime import datetime
import binascii

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
        output_group.add_argument("-a", "--use-ascii", action="store_true", dest="use_ascii", help="Use ASCII format for output file")

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
        sc_encode.add_argument("-m", "--material", action="store", dest="material", nargs="+", type=str, choices=CodeMaterial.all())
        sc_encode.add_argument("-v", "--version", action="store", dest="version")
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

    def _make_info(self, args, cartridge, machine_number):
        l = []
        if args.input_file != None:
            l.append("Cartridge - '" + args.input_file + "'")
            l.append("-"*79)
        l.append("Serial number\t\t" + str(cartridge.serial_number))
        material_id = material.get_id_from_name(cartridge.material_name)
        l.append("Material\t\t" + cartridge.material_name + " (" + str(material_id) + " - " + hex(material_id) +")")
        l.append("Manufacturing lot\t" + str(cartridge.manufacturing_lot))
        l.append("Manufacturing date\t" + str(cartridge.manufacturing_date))
        l.append("Last use date\t\t" + str(cartridge.use_date))
        l.append("Initial quantity\t" + str(cartridge.initial_material_quantity))
        l.append("Current quantity\t" + str(cartridge.current_material_quantity))
        l.append("Key fragment\t\t" + str(cartridge.key_fragment))
        l.append("Version\t\t\t" + str(cartridge.version))
        l.append("Signature\t\t" + str(cartridge.signature))
        l.append("")
        l.append("Machine type:\t\t" + str(args.machine_type) + " " + str(machine_number))
        l.append("EEPROM uid:\t\t" + str(args.eeprom_uid))
        return l

    def _make_recreate(self, args, cartridge):
        l = []
        l.append("To recreate this cartridge:")
        l.append("stratasys-cli.py eeprom")
        l.append(" --output-file XXX_REPLACE_ME_XXX")
        if args.use_ascii == True: l.append(" --use-ascii")
        l.append(" --machine-type " + str(args.machine_type))
        l.append(" --eeprom-uid " + str(args.eeprom_uid))
        l.append(" --serial-number " + str(cartridge.serial_number))
        l.append(" --material-name " + str(cartridge.material_name))
        l.append(" --manufacturing-lot " + str(cartridge.manufacturing_lot))
        l.append(" --manufacturing-date \"" + str(cartridge.manufacturing_date) + "\"")
        l.append(" --use-date \"" + str(cartridge.use_date) + "\"")
        l.append(" --initial-material " + str(cartridge.initial_material_quantity))
        l.append(" --current-material " + str(cartridge.current_material_quantity))
        l.append(" --key-fragment " + str(cartridge.key_fragment))
        l.append(" --version " + str(cartridge.version))
        l.append(" --signature " + str(cartridge.signature))
        return l

    def _make_ascii(self, args, cartridge, eeprom_bin, machine_number):
        s = ''

        # add comments
        lines = []
        lines = self._make_info(args, cartridge, machine_number)
        if args.recreate_input_file:
            lines.append('')
            lines.extend(self._make_recreate(args, cartridge))
        lines.append('')
        for l in lines: s += '# ' + l + '\n'

        # turn to binary into 32 chars wide ascii lines
        eeprom_ascii = binascii.b2a_hex(eeprom_bin)
        n = len(eeprom_ascii)
        for i in range(0, n, 32):
            nn = 32
            if (n - i) < 32: nn = n - i
            s += eeprom_ascii[i : i + nn] + '\n'

        return s

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

        mode = "w"
        if args.use_ascii == True: eeprom = self._make_ascii(args, cart, eeprom, machine_number)
        else: mode += "b"

        f = open(args.output_file, mode)
        f.write(eeprom)
        f.close()
        return

    def _eeprom_info(self, args):
        f = open(args.input_file, "rb")
        cartridge_crypted = bytearray(f.read())
        f.close()

        m = manager.Manager(crypto.Desx_Crypto(), checksum.Crc16_Checksum())
        machine_number = machine.get_number_from_type(args.machine_type)
        cartridge = m.decode(machine_number, args.eeprom_uid, cartridge_crypted)

        lines = self._make_info(args, cartridge, machine_number)
        if args.recreate_input_file:
            lines.append('')
            lines.extend(self._make_recreate(args, cartridge))
        lines.append('')
        for l in lines: print(l)

        return

    def _material_list(self, args):
        for k in range(len(material.id_to_name)):
            m = material.id_to_name[k]
            if m != "unknown":
                print(str(k) + "\t" + m)

    def _setupcode_encode(self, args):
        encoder = SetupcodeEncoder()
        encoder.encode(args.serial_number, args.system_type, args.envelope_size, args.build_speed, args.material, args.code_type, args.version, args.key)

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
