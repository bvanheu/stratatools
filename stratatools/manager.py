#
# See the LICENSE file
#

import datetime
import struct
import time
import binascii

import cartridge_pb2
import material

from crypto import Desx_Crypto, Xor_Crypto

#
# CartridgeManager is used to create, encrypt and decrypt Stratasys cartridge
#
# Typical structure on the EEPROM
#        offset : len
#        0x00   : 0x08 - Canister serial number (double) (part of the key, written *on* the canister as S/N)
#        0x08   : 0x08 - Material type (double)
#        0x10   : 0x14 - Manufacturing lot (string)
#        0x24   : 0x02 - Version? (must be 1)
#        0x28   : 0x08 - Manufacturing date (date yymmddhhmmss)
#        0x30   : 0x08 - Use date (date yymmddhhmmss)
#        0x38   : 0x08 - Initial material quantity (double)
#        0x40   : 0x02 - Plain content CRC (uint16)
#        0x46   : 0x02 - Crypted content CRC (uint16)
#        0x48   : 0x08 - Key (unencrypted, 8 bytes)
#        0x50   : 0x02 - Key CRC (unencrypted, uint16)
#        0x58   : 0x08 - Current material quantity (double)
#        0x60   : 0x02 - Current material quantity crypted CRC (unencrypted, uint16)
#        0x62   : 0x02 - Current material quantity CRC (unencrypted, uint16)
#       ~~~~~~~~~~~~~
#       14 0x00: 0x48 - crypted/plaintext (start, len)
#       15 0x58: 0x10 - unknown, looks like DEX IV, but why?
#       16 0x48: 0x10 - ^

class Manager_v1:
    def __init__(self, crypto, checksum):
        self.crypto = crypto
        self.checksum = checksum

    #
    # Encode a cartridge object into a data that can be burn onto a cartridge
    #
    def encode(self, machine_number, eeprom_uid, cartridge):
        cartridge_packed = self.pack(cartridge)
        cartridge_crypted = self.encrypt(machine_number, eeprom_uid, cartridge_packed)
        return cartridge_crypted

    #
    # Decode a eeprom to a cartridge object
    #
    def decode(self, machine_number, eeprom_uid, cartridge_crypted):
        cartridge_packed = self.decrypt(machine_number, eeprom_uid, cartridge_crypted)
        cartridge = self.unpack(cartridge_packed)
        return cartridge

    #
    # Pack a cartridge into a format suitable to be encrypted then burn
    # onto the cartridge EEPROM
    #
    def pack(self, cartridge):
        eeprom = bytearray(0x71)

        # serial number
        struct.pack_into("<d", eeprom, 0x0, cartridge.serial_number)
        # material id
        struct.pack_into("<d", eeprom, 0x08, material.get_id_from_name(cartridge.material_name))
        # manufacturing lot
        struct.pack_into("<20s", eeprom, 0x10, str(cartridge.manufacturing_lot))
        # version (not sure)
        struct.pack_into("<H", eeprom, 0x24, cartridge.version)
        # manufacturing date
        mfg_dt = cartridge.manufacturing_date.ToDatetime()
        struct.pack_into("<HBBBBH", eeprom, 0x28,
                mfg_dt.year - 1900,
                mfg_dt.month,
                mfg_dt.day,
                mfg_dt.hour,
                mfg_dt.minute,
                mfg_dt.second)
        # last use date
        lu_dt = cartridge.last_use_date.ToDatetime()
        struct.pack_into("<HBBBBH", eeprom, 0x30,
                lu_dt.year - 1900,
                lu_dt.month,
                lu_dt.day,
                lu_dt.hour,
                lu_dt.minute,
                lu_dt.second)
        struct.pack_into("<d", eeprom, 0x38, cartridge.initial_material_quantity)
        # plaintext checksum
        struct.pack_into("<H", eeprom, 0x40, self.checksum.checksum(eeprom[0x00:0x40]))
        # key
        struct.pack_into("<8s", eeprom, 0x48, str(cartridge.key_fragment.decode("hex")))
        # key checksum
        struct.pack_into("<H", eeprom, 0x50, self.checksum.checksum(eeprom[0x48:0x50]))
        # current material quantity
        struct.pack_into("<d", eeprom, 0x58, cartridge.current_material_quantity)
        # Checksum current material quantity
        struct.pack_into("<H", eeprom, 0x62, self.checksum.checksum(eeprom[0x58:0x60]))
        # signature (not sure, not usedu)
        struct.pack_into("<9s", eeprom, 0x68, str(cartridge.signature))

        return eeprom

    #
    # Unpack a decrypted cartridge into a catridge object
    #
    def unpack(self, cartridge_packed):
        # Validating plaintext checksum
        if self.checksum.checksum(cartridge_packed[0x00:0x40]) != struct.unpack("<H", str(cartridge_packed[0x40:0x42]))[0]:
            raise Exception("invalid content checksum: should have " + hex(struct.unpack("<H", str(cartridge_packed[0x40:0x42]))[0]) + " but have " + hex(self.checksum.checksum(cartridge_packed[0x00:0x40])))

        # Validating current material quantity checksum
        if self.checksum.checksum(cartridge_packed[0x58:0x60]) != struct.unpack("<H", str(cartridge_packed[0x62:0x64]))[0]:
            raise Exception("invalid current material quantity checksum")

        cartridge_packed = buffer(cartridge_packed)

        # Serial number
        serial_number = struct.unpack_from("<d", cartridge_packed, 0x0)[0]
        # Material
        material_name = material.get_name_from_id(int(struct.unpack_from("<d", cartridge_packed, 0x08)[0]))
        # Manufacturing lot
        manufacturing_lot = struct.unpack_from("<20s", cartridge_packed, 0x10)[0].split('\x00')[0]
        # Manufacturing datetime
        (mfg_datetime_year,
            mfg_datetime_month,
            mfg_datetime_day,
            mfg_datetime_hour,
            mfg_datetime_minute,
            mfg_datetime_second) = struct.unpack_from("<HBBBBH", cartridge_packed, 0x28)
        mfg_datetime = datetime.datetime(mfg_datetime_year + 1900,
                mfg_datetime_month,
                mfg_datetime_day,
                mfg_datetime_hour,
                mfg_datetime_minute,
                mfg_datetime_second)
        # Last use datetime
        (use_datetime_year,
            use_datetime_month,
            use_datetime_day,
            use_datetime_hour,
            use_datetime_minute,
            use_datetime_second) = struct.unpack_from("<HBBBBH", cartridge_packed, 0x30)
        use_datetime = datetime.datetime(use_datetime_year + 1900,
                use_datetime_month,
                use_datetime_day,
                use_datetime_hour,
                use_datetime_minute,
                use_datetime_second)
        # Initial material quantity
        initial_material_quantity = struct.unpack_from("<d", cartridge_packed, 0x38)[0]
        # Version
        version = struct.unpack_from("<H", cartridge_packed, 0x24)[0]
        # Key fragment
        key_fragment = str(struct.unpack_from("<8s", cartridge_packed, 0x48)[0]).encode("hex")
        # Current material quantity
        current_material_quantity = struct.unpack_from("<d", cartridge_packed, 0x58)[0]
        # Signature
        signature = struct.unpack_from("<9s", cartridge_packed, 0x68)[0]

        c = cartridge_pb2.Cartridge()
        c.serial_number = serial_number
        c.material_name = material_name
        c.manufacturing_lot = manufacturing_lot
        c.manufacturing_date.FromDatetime(mfg_datetime)
        c.last_use_date.FromDatetime(use_datetime)
        c.initial_material_quantity = initial_material_quantity
        c.current_material_quantity = current_material_quantity
        c.key_fragment = key_fragment
        c.version = version
        c.signature = signature

        return c

    #
    # Encrypt a packed cartridge into a crypted cartridge
    #
    def encrypt(self, machine_number, eeprom_uid, cartridge_packed):
        cartridge_crypted = cartridge_packed

        # Validate key fragment checksum
        # TODO

        # Build the key
        key = self.build_key(cartridge_packed[0x48:0x50], machine_number, eeprom_uid)
        # Encrypt content
        struct.pack_into("<64s", cartridge_crypted, 0x00, str(self.crypto.encrypt(key, cartridge_packed[0x00:0x40])))
        # Checksum crypted content
        struct.pack_into("<H", cartridge_crypted, 0x46, self.checksum.checksum(cartridge_packed[0x00:0x40]))
        # Encrypt current material quantity
        struct.pack_into("<8s", cartridge_crypted, 0x58, str(self.crypto.encrypt(key, cartridge_packed[0x58:0x60])))
        # Checksum crypted current material quantity
        struct.pack_into("<H", cartridge_crypted, 0x60, self.checksum.checksum(cartridge_packed[0x58:0x60]))

        return cartridge_crypted

    #
    # Decrypt a crypted cartridge into a packed cartridge
    #
    def decrypt(self, machine_number, eeprom_uid, cartridge_crypted):
        cartridge_packed = cartridge_crypted

        # Validate key fragment checksum
        # TODO

        # Build the key
        key = self.build_key(cartridge_crypted[0x48:0x50], machine_number, eeprom_uid)
        # Validate crypted content checksum
        if self.checksum.checksum(cartridge_crypted[0x00:0x40]) != struct.unpack("<H", str(cartridge_crypted[0x46:0x48]))[0]:
            raise Exception("invalid crypted content checksum")
        # Decrypt content
        cartridge_packed[0x00:0x40] = self.crypto.decrypt(key, cartridge_crypted[0x00:0x40])
        # Validate crypted current material quantity checksum
        if self.checksum.checksum(cartridge_crypted[0x58:0x60]) != struct.unpack("<H", str(cartridge_crypted[0x60:0x62]))[0]:
            raise Exception("invalid current material quantity checksum")
        # Decrypt current material quantity
        cartridge_packed[0x58:0x60] = self.crypto.decrypt(key, cartridge_crypted[0x58:0x60])

        return cartridge_packed

    #
    # Build a key used to encrypt/decrypt a cartridge
    #
    def build_key(self, cartridge_key, machine_number, eeprom_uid):
        machine_number = bytearray(machine_number)
        eeprom_uid = bytearray(eeprom_uid)
        key = bytearray(16)

        key[0] = ~cartridge_key[0] & 0xff
        key[1] = ~cartridge_key[2] & 0xff
        key[2] = ~eeprom_uid[2] & 0xff
        key[3] = ~cartridge_key[6] & 0xff
        key[4] = ~machine_number[0] & 0xff
        key[5] = ~machine_number[2] & 0xff
        key[6] = ~eeprom_uid[6] & 0xff
        key[7] = ~machine_number[6] & 0xff
        key[8] = ~machine_number[7] & 0xff
        key[9] = ~eeprom_uid[1] & 0xff
        key[10] = ~machine_number[3] & 0xff
        key[11] = ~machine_number[1] & 0xff
        key[12] = ~cartridge_key[7] & 0xff
        key[13] = ~eeprom_uid[5] & 0xff
        key[14] = ~cartridge_key[3] & 0xff
        key[15] = ~cartridge_key[1] & 0xff

        return key

# Typical structure on the EEPROM
#        offset : len
#        0x00   :   0x08    - Current Material Quantity
#        0x08   ;   0x02    - Encrypted Current Material Quantity CRC
#        0x0A   :   0x02    - Decrypted Current Material Quantity CRC
#        0x02   :   0x01
#        0x13   :   0x02    - Key Fragment CRC (0x14d0)
#        0x15   :   0x02
#        0x17   :   0x08    - Key Fragment
#        0x1f   :   0x01
#        0x20   :   0x08    - Initial use date
#        0x28   :   0x08    - Manufacturing date
#        0x30   :   0x08    - Serial number
#        0x38   :   0x08    - Material type
#        0x40   :   0x14    - Manufacturing lot
#        0x54   :   0x02    - Eeprom version
#        0x56   :   0x02
#        0x58   :   0x08    - Initial material qty
#        0x60   :   0x02    - Decrypted Info Block CRC
#        0x62   :   0x02
#        0x64   :   0x02    - Encrypted Info Block CRC
#        0x66   :   0x02    -
#        0x68   :   0x20    - Signature
#        0x78   :   0x08    - Encrypted serial number
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#        0x20   :   0x40    - Info Block
#        0x00   :   0x08    - Current Material Quantity
#        0x78   :   0x08    - Encrypted Serial Number


# Field table
# -----------
# #    offset   length  name
# 0     0x68    0x09    Signature
# 1     0x68    0x10
# 2     0x00    0x08    Current material qty
# 3     0x08    0x02
# 4     0x0A    0x02    Decrypted material qty CRC
# 5     0x20    0x48    Info block
# 6     0x66    0x02
# 7     0x60    0x02
# 8     0x20    0x08    Initial use date
# 9     0x58    0x08    Iniial material qty
# a     0x10    0x10
# b     0x13    0x02    Key framgnet crc
# c     0x17    0x08    Key fragment
# d     0x00    0x10
# e     0x38    0x08    Material type
# f     0x28    0x08    Manufacturing date
# 10    0x40    0x14    Manufacturing lot
# 11    0x30    0x08    Serial Number
# 12    0x78    0x08    Encrypted Serial Number ?
# 13    0x78    0x08    ^
# 14    0x54    0x02    Eprom version?

class Manager_v3:
    def __init__(self, crypto, checksum):
        self.crypto = crypto
        self.checksum = checksum
        self.block1_xor_key = [0x07, 0x44, 0xDD, 0x84, 0xB5, 0x80, 0xA8, 0x9C]
        self.block2_xor_key = [0xc0, 0xd3, 0x21, 0xa4, 0x41, 0x77, 0x22, 0xcb]
        self.block3_xor_key = [0xaf, 0xa04, 0xea, 0xd1, 0x5d, 0x52, 0x40, 0x3a]

    def encode(self, machine_number, eeprom_uid, cartridge):
        cartridge_packed = self.pack(cartridge)
        cartridge_crypted = self.encrypt(machine_number, eeprom_uid, cartridge_packed)
        return cartridge_crypted

    #
    # Decode a eeprom to a cartridge object
    #
    def decode(self, machine_number, eeprom_uid, cartridge_crypted):
        cartridge_packed = self.decrypt(machine_number, eeprom_uid, cartridge_crypted)
        cartridge = self.unpack(cartridge_packed)
        return cartridge

    #
    # Encrypt a packed cartridge into a crypted cartridge
    #
    def encrypt(self, machine_number, eeprom_uid, cartridge_packed):
        cartridge_crypted = cartridge_packed

        # Build the key
        key_fragment = self.shuffle_key_fragment(cartridge_crypted[0x17:0x1f])
        key = self.build_key(key_fragment, machine_number, eeprom_uid)

        desx = Desx_Crypto()
        xor = Xor_Crypto()

        desx_key = key[0:8] + key[15:23]

        #
        # Block 1 - info block
        #
        intermediate = bytearray(8)
        intermediate_key = self.block1_xor_key

        for i in range(0, 8):
            beg = int(0x20 + (i * 8))
            end = int(0x20 + ((i * 8) + 8))

            cartridge_crypted[beg:end] = xor.encrypt(intermediate_key, cartridge_packed[beg:end])
            cartridge_crypted[beg:end] = desx.encrypt(desx_key, cartridge_crypted[beg:end])
            intermediate_key = cartridge_crypted[beg:end]

        struct.pack_into("<H", cartridge_crypted, 0x66, self.checksum.checksum(cartridge_crypted[0x20:0x60]))

        #
        # Block 2 - Encrypted Material Qty
        #
        cartridge_crypted[0x00:0x08] = xor.encrypt(self.block2_xor_key, cartridge_packed[0x00:0x08])
        cartridge_crypted[0x00:0x08] = desx.encrypt(desx_key, cartridge_crypted[0x00:0x08])

        struct.pack_into("<H", cartridge_crypted, 0x08, self.checksum.checksum(cartridge_crypted[0x00:0x08]))

        #
        # Block 3 - Encrypted Serial Number
        #
        key1 = self.shuffle_key(key, 23, 29)
        desx_key1 = key1[0:8] + key1[15:23]

        key2 = self.shuffle_key(key1, 23, 29)
        desx_key2 = key2[0:8] + key2[15:23]

        key3 = self.shuffle_key(key2, 23, 29)
        desx_key3 = key3[0:8] + key3[15:23]

        cartridge_crypted[0x78:0x80] = xor.encrypt(self.block3_xor_key, cartridge_packed[0x78:0x80])
        cartridge_crypted[0x78:0x80] = desx.encrypt(desx_key1, cartridge_crypted[0x78:0x80])
        cartridge_crypted[0x78:0x80] = desx.decrypt(desx_key2, cartridge_crypted[0x78:0x80])
        cartridge_crypted[0x78:0x80] = desx.encrypt(desx_key3, cartridge_crypted[0x78:0x80])

        return cartridge_crypted

    #
    # Decrypt a crypted cartridge into a packed cartridge
    #
    def decrypt(self, machine_number, eeprom_uid, cartridge_crypted):
        cartridge_packed = bytearray(cartridge_crypted)

        # Validate crypted content checksum
        checksum1 = self.checksum.checksum(cartridge_crypted[0x17:0x1f], 0x14d0)
        checksum2 = struct.unpack("<H", str(cartridge_crypted[0x13:0x15]))[0]
        if checksum1 != checksum2:
            raise Exception("invalid keyfrag crc calculated " + hex(checksum1) + " but expected " + hex(checksum2))

        key_fragment = self.shuffle_key_fragment(cartridge_crypted[0x17:0x1f])

        key = self.build_key(key_fragment, machine_number, eeprom_uid)
        desx_key = key[0:8] + key[15:23]

        desx = Desx_Crypto()
        xor = Xor_Crypto()

        #
        # Block 1 - Info block
        #
        checksum1 = self.checksum.checksum(cartridge_crypted[0x20:0x60])
        checksum2 = struct.unpack("<H", str(cartridge_crypted[0x66:0x68]))[0]

        if checksum1 != checksum2:
            raise Exception("invalid crypted info block crc: calculated " + hex(checksum1) + " but expected " + hex(checksum2))

        intermediate = bytearray(8)
        intermediate_key = self.block1_xor_key

        for i in range(0, 8):
            beg = int(0x20 + (i * 8))
            end = int(0x20 + ((i * 8) + 8))

            intermediate = desx.decrypt(desx_key, cartridge_crypted[beg:end])
            cartridge_packed[beg:end] = xor.decrypt(intermediate_key, intermediate)
            intermediate_key = cartridge_crypted[beg:end]

        checksum1 = self.checksum.checksum(cartridge_packed[0x20:0x60])
        checksum2 = struct.unpack("<H", str(cartridge_crypted[0x60:0x62]))[0]
        if checksum1 != checksum2:
            raise Exception("invalid plaintext crc: calculated " + hex(checksum1) + " but expected " + hex(checksum2))

        #
        # Block 2 - Encrypted material qty
        #
        checksum1 = self.checksum.checksum(cartridge_crypted[0:8])
        checksum2 = struct.unpack("<H", str(cartridge_crypted[8:10]))[0]

        if checksum1 != checksum2:
            raise Exception("invalid crypted current material crc: calculated " + hex(checksum1) + " but expected " + hex(checksum2))

        cartridge_packed[0x00:0x08] = desx.decrypt(desx_key, cartridge_crypted[0x00:0x08])
        cartridge_packed[0x00:0x08] = xor.decrypt(self.block2_xor_key, cartridge_packed[0x00:0x08])

        checksum1 = self.checksum.checksum(cartridge_packed[0x00:0x08])
        checksum2 = struct.unpack("<H", str(cartridge_crypted[0x0a:0x0c]))[0]
        if checksum1 != checksum2:
            raise Exception("invalid decrypted material qty crc: calculated " + hex(checksum1) + " but expected " + hex(checksum2))

        #
        # Block 3 - Encrypted serial number
        #
        key1 = self.shuffle_key(key, 23, 29)
        desx_key1 = key1[0:8] + key1[15:23]

        key2 = self.shuffle_key(key1, 23, 29)
        desx_key2 = key2[0:8] + key2[15:23]

        key3 = self.shuffle_key(key2, 23, 29)
        desx_key3 = key3[0:8] + key3[15:23]

        cartridge_packed[0x78:0x80] = desx.decrypt(desx_key3, cartridge_crypted[0x78:0x80])
        cartridge_packed[0x78:0x80] = desx.encrypt(desx_key2, cartridge_packed[0x78:0x80])
        cartridge_packed[0x78:0x80] = desx.decrypt(desx_key1, cartridge_packed[0x78:0x80])
        cartridge_packed[0x78:0x80] = xor.decrypt(self.block3_xor_key, cartridge_packed[0x78:0x80])

        if cartridge_packed[0x30:0x38] != cartridge_packed[0x78:0x80]:
            raise Exception("invalid decryped serial number: decrypted " + binascii.hexlify(cartridge_packed[0x78:0x80]) + " but expected " + binascii.hexlify(cartridge_packed[0x30:0x38]))

        return cartridge_packed

    #
    # Pack a cartridge into a format suitable to be encrypted then burn
    # onto the cartridge EEPROM
    #
    def pack(self, cartridge):
        eeprom = bytearray(0x88)

        # current material quantity
        struct.pack_into("<d", eeprom, 0x00, cartridge.current_material_quantity)
        # key fragment
        struct.pack_into("<8s", eeprom, 0x17, str(cartridge.key_fragment.decode("hex")))
        # last use date
        lu_dt = cartridge.last_use_date.ToDatetime()
        struct.pack_into("<HBBBBH", eeprom, 0x20,
                lu_dt.year - 1900,
                lu_dt.month,
                lu_dt.day,
                lu_dt.hour,
                lu_dt.minute,
                lu_dt.second)
        # manufacturing date
        mfg_dt = cartridge.manufacturing_date.ToDatetime()
        struct.pack_into("<HBBBBH", eeprom, 0x28,
                mfg_dt.year - 1900,
                mfg_dt.month,
                mfg_dt.day,
                mfg_dt.hour,
                mfg_dt.minute,
                mfg_dt.second)
        # serial number
        struct.pack_into("<d", eeprom, 0x30, cartridge.serial_number)
        # material id
        struct.pack_into("<d", eeprom, 0x38, material.get_id_from_name(cartridge.material_name))
        # manufacturing lot
        struct.pack_into("<20s", eeprom, 0x40, str(cartridge.manufacturing_lot))
        # version
        struct.pack_into("<H", eeprom, 0x54, cartridge.version)
        # initial material qty
        struct.pack_into("<d", eeprom, 0x58, cartridge.initial_material_quantity)
        # signature
        struct.pack_into("<9s", eeprom, 0x68, str(cartridge.signature))

        # checksum block info
        struct.pack_into("<H", eeprom, 0x60, self.checksum.checksum(eeprom[0x20:0x60]))
        # checksum key fragment
        struct.pack_into("<H", eeprom, 0x13, self.checksum.checksum(eeprom[0x17:0x1f], 0x14d0))
        # checksum current material quantity
        struct.pack_into("<H", eeprom, 0x0a, self.checksum.checksum(eeprom[0x00:0x08]))

        # Put a duplicate serial number to make it easier to encrypt the payload.
        struct.pack_into("<d", eeprom, 0x78, cartridge.serial_number)

        return eeprom

    #
    # Unpack a decrypted cartridge into a catridge object
    #
    def unpack(self, cartridge_packed):
        ## Validating plaintext checksum
        #if self.checksum.checksum(cartridge_packed[0x00:0x40]) != struct.unpack("<H", str(cartridge_packed[0x40:0x42]))[0]:
        #    raise Exception("invalid content checksum: should have " + hex(struct.unpack("<H", str(cartridge_packed[0x40:0x42]))[0]) + " but have " + hex(self.checksum.checksum(cartridge_packed[0x00:0x40])))

        ## Validating current material quantity checksum
        #if self.checksum.checksum(cartridge_packed[0x58:0x60]) != struct.unpack("<H", str(cartridge_packed[0x62:0x64]))[0]:
        #    raise Exception("invalid current material quantity checksum")

        cartridge_packed = buffer(cartridge_packed)

        # Current material quantity
        current_material_quantity = struct.unpack_from("<d", cartridge_packed, 0x00)[0]
        # Key fragment
        key_fragment = str(struct.unpack_from("<8s", cartridge_packed, 0x17)[0]).encode("hex")
        # Last use datetime
        (use_datetime_year,
            use_datetime_month,
            use_datetime_day,
            use_datetime_hour,
            use_datetime_minute,
            use_datetime_second) = struct.unpack_from("<HBBBBH", cartridge_packed, 0x20)
        use_datetime = datetime.datetime(use_datetime_year + 1900,
                use_datetime_month,
                use_datetime_day,
                use_datetime_hour,
                use_datetime_minute,
                use_datetime_second)
        # Manufacturing datetime
        (mfg_datetime_year,
            mfg_datetime_month,
            mfg_datetime_day,
            mfg_datetime_hour,
            mfg_datetime_minute,
            mfg_datetime_second) = struct.unpack_from("<HBBBBH", cartridge_packed, 0x28)
        mfg_datetime = datetime.datetime(mfg_datetime_year + 1900,
                mfg_datetime_month,
                mfg_datetime_day,
                mfg_datetime_hour,
                mfg_datetime_minute,
                mfg_datetime_second)
        # Serial number
        serial_number = struct.unpack_from("<d", cartridge_packed, 0x30)[0]
        # Material
        material_name = material.get_name_from_id(int(struct.unpack_from("<d", cartridge_packed, 0x38)[0]))
        # Manufacturing lot
        manufacturing_lot = struct.unpack_from("<20s", cartridge_packed, 0x40)[0].split('\x00')[0]
        # Eprom version
        version = struct.unpack_from("<H", cartridge_packed, 0x54)[0]
        # Initial material quantity
        initial_material_quantity = struct.unpack_from("<d", cartridge_packed, 0x58)[0]
        # Signature
        signature = struct.unpack_from("<9s", cartridge_packed, 0x68)[0]

        c = cartridge_pb2.Cartridge()
        c.serial_number = serial_number
        c.material_name = material_name
        c.manufacturing_lot = manufacturing_lot
        c.manufacturing_date.FromDatetime(mfg_datetime)
        c.last_use_date.FromDatetime(use_datetime)
        c.initial_material_quantity = initial_material_quantity
        c.current_material_quantity = current_material_quantity
        c.key_fragment = key_fragment
        c.version = version
        c.signature = signature

        return c

    # EEPROM ID must start with family code, end with checksum
    def build_key(self, cartridge_key, machine_number, eeprom_uid):
        machine_number = bytearray(machine_number.decode("hex"))
        # [0]      [1]  [6]  [7]
        # [family] [b0] [b6] [checksum]
        eeprom_uid = bytearray(eeprom_uid.decode("hex"))
        key = bytearray(23)

        key[0] = ~eeprom_uid[3] & 0xff
        key[1] = ~machine_number[3] & 0xff
        key[2] = ~machine_number[1] & 0xff
        key[3] = ~cartridge_key[0] & 0xff
        key[4] = ~cartridge_key[1] & 0xff
        key[5] = ~cartridge_key[2] & 0xff
        key[6] = ~eeprom_uid[5] & 0xff
        key[7] = ~cartridge_key[3] & 0xff
        key[8] = ~machine_number[7] & 0xff
        key[9] = ~machine_number[5] & 0xff
        key[10] = ~machine_number[2] & 0xff
        key[11] = ~eeprom_uid[1] & 0xff
        key[12] = ~eeprom_uid[4] & 0xff
        key[13] = ~cartridge_key[4] & 0xff
        key[14] = ~cartridge_key[5] & 0xff
        key[15] = ~eeprom_uid[6] & 0xff
        key[16] = ~cartridge_key[6] & 0xff
        key[17] = ~machine_number[0] & 0xff
        key[18] = ~machine_number[6] & 0xff
        key[19] = ~eeprom_uid[0] & 0xff
        key[20] = ~machine_number[4] & 0xff
        key[21] = ~cartridge_key[7] & 0xff
        key[22] = ~eeprom_uid[2] & 0xff

        return key

    def shuffle_key_fragment(self, key_fragment):
        shuffled_key_fragment = bytearray(8)

        shuffled_key_fragment[0] = key_fragment[5]
        shuffled_key_fragment[1] = key_fragment[6]
        shuffled_key_fragment[2] = key_fragment[1]
        shuffled_key_fragment[3] = key_fragment[0]
        shuffled_key_fragment[4] = key_fragment[3]
        shuffled_key_fragment[5] = key_fragment[4]
        shuffled_key_fragment[6] = key_fragment[7]
        shuffled_key_fragment[7] = key_fragment[2]

        return shuffled_key_fragment

    def shuffle_key(self, key, key_length, int2):
        remaining = int2 % (8 * key_length)

        # Rotation
        if (remaining > 7):
            shift = remaining / 8
            key = key[key_length-shift:] + key[:key_length-shift]
            remaining = remaining - (8 * shift)

        # Bit shift
        if remaining > 0:
            shift_value = 8 - remaining

            char_end_of_key = key[key_length-1]

            key[key_length-1] = (char_end_of_key >> remaining) & 0xff

            for i in range(22, 0, -1):
                c = key[i-1]
                key[i] |= (c << shift_value) & 0xff
                key[i-1] = (c >> remaining) & 0xff

            key[0] |= (char_end_of_key << shift_value) & 0xff

        return key
