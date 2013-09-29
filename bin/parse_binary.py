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

material_id_to_name = ["unknown (please contribute)"] * 0x100
material_id_to_name[0x00] = "ABS"
material_id_to_name[0x01] = "ABS_RED"
material_id_to_name[0x02] = "ABS_GRN"
material_id_to_name[0x03] = "ABS_BLK"
material_id_to_name[0x04] = "ABS_YEL"
material_id_to_name[0x05] = "ABS_BLU"
material_id_to_name[0x06] = "ABS_CST"
material_id_to_name[0x07] = "ABSI"
material_id_to_name[0x08] = "ABSI_RED"
material_id_to_name[0x09] = "ABSI_GRN"
material_id_to_name[0x0a] = "ABSI_BLK"
material_id_to_name[0x0b] = "ABSI_YEL"
material_id_to_name[0x0c] = "ABSI_BLU"
material_id_to_name[0x0d] = "ABSI_AMB",
material_id_to_name[0x0e] = "ABSI_CST"
material_id_to_name[0x0f] = "ABS_S"
material_id_to_name[0x10] = "PC"
material_id_to_name[0x11] = "PC_RED"
material_id_to_name[0x12] = "PC_GRN"
material_id_to_name[0x13] = "PC_BLK"
material_id_to_name[0x14] = "PC_YEL"
material_id_to_name[0x15] = "PC_BLU",
material_id_to_name[0x16] = "PC_CST"
material_id_to_name[0x17] = "PC_S"
material_id_to_name[0x18] = "ULT9085"
material_id_to_name[0x19] = "ULT_RED"
material_id_to_name[0x1a] = "ULT_GRN"
material_id_to_name[0x1b] = "ULT_BLK"
material_id_to_name[0x1c] = "ULT_YEL"
material_id_to_name[0x1d] = "ULT_BLU"
material_id_to_name[0x1e] = "ULT_CST"
material_id_to_name[0x1f] = "ULT_S"
material_id_to_name[0x20] = "PPSF"
material_id_to_name[0x21] = "PPSF_RED"
material_id_to_name[0x22] = "PPSF_GRN"
material_id_to_name[0x23] = "PPSF_BLK"
material_id_to_name[0x24] = "PPSF_YEL"
material_id_to_name[0x25] = "PPSF_BLU"
material_id_to_name[0x26] = "PPSF_CST"
material_id_to_name[0x27] = "PPSF_S"
material_id_to_name[0x28] = "ABS_SS"
material_id_to_name[0x29] = "P401"
material_id_to_name[0x2a] = "P401_RED"
material_id_to_name[0x2b] = "P401_GRN"
material_id_to_name[0x2c] = "P401_BLK"
material_id_to_name[0x2d] = "P401_YEL"
material_id_to_name[0x2e] = "P401_BLU"
material_id_to_name[0x2f] = "P401_CST"
material_id_to_name[0x30] = "ABS_SGRY"
material_id_to_name[0x31] = "ABS_GRY"
material_id_to_name[0x33] = "ABSI_GRY"
material_id_to_name[0x50] = "ABS-M30I"
material_id_to_name[0x51] = "ABS-ESD7"
material_id_to_name[0x64] = "PCABSWHT"
material_id_to_name[0x65] = "PCABSRED"
material_id_to_name[0x66] = "PCABSGRN"
material_id_to_name[0x67] = "PC-ABS"
material_id_to_name[0x68] = "PCABSYEL"
material_id_to_name[0x69] = "PCABSBLU"
material_id_to_name[0x6a] = "PCABSCST"
material_id_to_name[0x6b] = "PCABSGRY"
material_id_to_name[0x78] = "SR20"
material_id_to_name[0x82] = "PC_SR"
material_id_to_name[0x8c] = "ABS-M30"
material_id_to_name[0x8d] = "M30_RED"
material_id_to_name[0x8e] = "M30_GRN"
material_id_to_name[0x8f] = "M30_BLK"
material_id_to_name[0x90] = "M30_YEL"
material_id_to_name[0x91] = "M30_BLU"
material_id_to_name[0x92] = "M30_CST"
material_id_to_name[0x93] = "M30_GRY"
material_id_to_name[0x94] = "M30_SGRY"
material_id_to_name[0x95] = "M30_WHT"
material_id_to_name[0x96] = "M30_SIL"
material_id_to_name[0xa0] = "ABS_S"
material_id_to_name[0xaa] = "ABS_SS"
material_id_to_name[0xab] = "SR30"
material_id_to_name[0xad] = "ULT_S2"
material_id_to_name[0xae] = "SR-100"
material_id_to_name[0xb4] = "PC-ISO"
material_id_to_name[0xbe] = "PC-ISO-T"
material_id_to_name[0xbf] = "P1_5M1"
material_id_to_name[0xc0] = "P1_5M2"
material_id_to_name[0xc1] = "P1_5M3"
material_id_to_name[0xc2] = "RD1"
material_id_to_name[0xc3] = "RD2",
material_id_to_name[0xc4] = "RD3"
material_id_to_name[0xc5] = "RD4"
material_id_to_name[0xc6] = "RD5"
material_id_to_name[0xc7] = "RD6"
material_id_to_name[0xc8] = "RD7"
material_id_to_name[0xc9] = "RD8"
material_id_to_name[0xca] = "RD9"
material_id_to_name[0xcb] = "RD10"

f_in = open(sys.argv[1])

data = f_in.read(512)

f_in.close()

canister_serial_number = struct.unpack("<d", data[0x0:0x08])[0]
print("Canister S/N: " + str(int(canister_serial_number)))
material_type = int(struct.unpack("<d", data[0x08:0x10])[0])
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
