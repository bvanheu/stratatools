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

from datetime import datetime

class Cartridge:
    def __init__(self, serial_number=0, material=None, manufacturing_lot="", manufacturing_date=datetime.today(), use_date=datetime.today(), initial_material_quantity=0.0, current_material_quantity=0.0, key_fragment=bytearray(8), version=0x1, signature="STRATASYS"):
        # Serial number
        self.serial_number = serial_number
        # Material (see material.py)
        self.material = material
        # Manufacturing lot
        self.manufacturing_lot = manufacturing_lot
        # Manufacturing date
        self.manufacturing_date = manufacturing_date
        # Last use date
        self.use_date = use_date
        # Initial material quantity, in cubic feet
        self.initial_material_quantity = initial_material_quantity
        # Remaining material quantity
        self.current_material_quantity = current_material_quantity
        # Key used to encrypt / decrypt
        self.key_fragment = key_fragment
        # Version
        self.version = version
        # Signature
        self.signature = signature

    def __unicode__(self):
        pass

