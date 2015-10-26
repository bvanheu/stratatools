#
# See the LICENSE file
#

from datetime import datetime

class Cartridge:
    def __init__(self, serial_number=0, material_name=None, manufacturing_lot="", manufacturing_date=datetime.today(), use_date=datetime.today(), initial_material_quantity=0.0, current_material_quantity=0.0, key_fragment=bytearray(8), version=0x1, signature="STRATASYS"):
        # Serial number
        self.serial_number = serial_number
        # Material (see material.py)
        self.material_name = material_name
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

