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
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import struct

material_id_to_name = {
        0x00: "ABS", 0x01: "ABS_RED", 0x02: "ABS_GRN",  0x03: "ABS_BLK", 0x04: "ABS_YEL", 0x05: "ABS_BLU", 0x06: "ABS_CST",
        0x07: "ABSI", 0x08: "ABSI_RED", 0x09: "ABSI_GRN", 0x0a: "ABSI_BLK", 0x0b: "ABSI_YEL", 0x0c: "ABSI_BLU", 0x0d: "ABSI_AMB",
        0x0e: "ABSI_CST", 0x0f: "ABS_S", 0x10: "PC", 0x11: "PC_RED", 0x12: "PC_GRN", 0x13: "PC_BLK", 0x14: "PC_YEL", 0x15: "PC_BLU",
        0x16: "PC_CST", 0x17: "PC_S", 0x18: "ULT9085", 0x19: "ULT_RED", 0x1a: "ULT_GRN", 0x1b: "ULT_BLK", 0x1c: "ULT_YEL", 0x1d: "ULT_BLU",
        0x1e: "ULT_CST", 0x1f: "ULT_S", 0x20: "PPSF", 0x21: "PPSF_RED", 0x22: "PPSF_GRN", 0x23: "PPSF_BLK", 0x24: "PPSF_YEL", 0x25: "PPSF_BLU",
        0x26: "PPSF_CST", 0x27: "PPSF_S", 0x28: "ABS_SS", 0x29: "P401", 0x2a: "P401_RED", 0x2b: "P401_GRN", 0x2c: "P401_BLK", 0x2d: "P401_YEL",
        0x2e: "P401_BLU", 0x2f: "P401_CST", 0x30: "ABS_SGRY", 0x31: "ABS_GRY", 0x32: "ABSI_GRY", 0x50: "ABS-M30I", 0x51: "ABS-ESD7", 0x64: "PCABSWHT",
        0x65: "PCABSRED", 0x66: "PCABSGRN", 0x67: "PC-ABS", 0x68: "PCABSYEL", 0x69: "PCABSBLU", 0x6a: "PCABSCST", 0x6b: "PCABSGRY", 0x78: "SR20",
        0x82: "PC_SR", 0x8c: "ABS-M30", 0x8d: "M30_RED", 0x8e: "M30_GRN", 0x8f: "M30_BLK", 0x90: "M30_YEL", 0x91: "M30_BLU", 0x92: "M30_CST",
        0x93: "M30_GRY", 0x94: "M30_SGRY", 0x95: "M30_WHT", 0x96: "M30_SIL", 0xa0: "ABS_S", 0xaa: "ABS_SS", 0xab: "SR30", 0xad: "ULT_S2",
        0xae: "SR-100", 0xb4: "PC-ISO", 0xbe: "PC-ISO-T", 0xbf: "P1_5M1", 0xc0: "P1_5M2", 0xc1: "P1_5M3", 0xc2: "RD1", 0xc3: "RD2",
        0xc4: "RD3", 0xc5: "RD4", 0xc6: "RD5", 0xc7: "RD6", 0xc8: "RD7", 0xc9: "RD8", 0xca: "RD9", 0xcb: "RD10", 0xcc: '\x00'
    }

f_in = open(sys.argv[1])

data = f_in.read(512)

f_in.close()

canister_serial_number = struct.unpack("<d", data[0x0:0x08])[0]
print("Canister S/N: " + str(int(canister_serial_number)))
material_type = struct.unpack("<d", data[0x08:0x10])[0]
print("Material type: " + material_id_to_name[material_type] + " ("+str(int(material_type))+")")
manufacturing_lot = struct.unpack("<8s", data[0x10:0x18])[0]
print("Manufacturing lot: " + str(manufacturing_lot.split('\x00')[0]))
(year, month, day, hour, minute, second) = struct.unpack("<HBBBBH", data[0x28:0x30])
print("Manufacturing date: " + str(year+1900) + "/" + str(month+1) + "/" + str(day) + " " + str(hour) + ":" + str(minute) + ":" + str(second))
(year, month, day, hour, minute, second) = struct.unpack("<HBBBBH", data[0x30:0x38])
print("Use date: " + str(year+1900) + "/" + str(month+1) + "/" + str(day) + " " + str(hour) + ":" + str(minute) + ":" + str(second))
initial_material_qty = struct.unpack("<d", data[0x38:0x40])[0]
print("Initial material qty: " + str(initial_material_qty))
current_material_qty = struct.unpack("<d", data[0x58:0x60])[0]
print("Current material qty: " + str(current_material_qty))
