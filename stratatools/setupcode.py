#
# See the LICENSE file
#

import argparse
import struct
import sys

# Format
# ------
#   00  sn1
#   01  system type
#   02  envelope size
#   03  build speed
#   04  -
#   05  material abs
#   06  sn2
#   07  checksum1
#   08  checksum2
#   09  -
#   10  material ppsf
#   11  material iso
#   12  sn3
#   13  version
#   14  -
#   15  code type
#   16  mat
#   17  key
#   18  sn4

class Setupcode():
    serial_number = ""
    system_type = ""
    envelope_size = ""
    build_speed = ""
    version = ""
    code_type = ""
    material = ""
    key = ""

    def __init__(self):
        pass

class CodeMaterial():
    id_to_material = ["unknown"] * 0x10
    id_to_material[0x00] = "ABS"
    id_to_material[0x01] = "PC-ABS"
    id_to_material[0x02] = "PC"
    id_to_material[0x03] = "PC-ISO"
    id_to_material[0x04] = "PPSF"
    id_to_material[0x05] = "ABS-M30"
    id_to_material[0x06] = "ABSI"
    id_to_material[0x07] = "ABS-M30I"
    id_to_material[0x08] = "ULT9085"
    id_to_material[0x09] = "ABS-ESD7"
    id_to_material[0x0A] = "NYLON"
    id_to_material[0x0B] = "RD1-RD2-RD3-RD4-RD5"

    @staticmethod
    def all():
        return list(set(CodeMaterial.id_to_material))

    @staticmethod
    def to_id(material):
        return CodeMaterial.id_to_material.index(material)

    @staticmethod
    def from_id(id):
        return CodeMaterial.id_to_material[id]

class EnvelopeSize():
    id_to_envelopesize = ["invalid"] * 0x3
    id_to_envelopesize[0x1] = "small"
    id_to_envelopesize[0x2] = "large"

    @staticmethod
    def all():
        return list(set(EnvelopeSize.id_to_envelopesize))

    @staticmethod
    def to_id(buildspeed):
        return EnvelopeSize.id_to_envelopesize.index(buildspeed)

    @staticmethod
    def from_id(id):
        return EnvelopeSize.id_to_envelopesize[id]

class BuildSpeed():
    id_to_buildspeed = ["invalid"] * 0x3
    id_to_buildspeed[0x1] = "1x"
    id_to_buildspeed[0x2] = "ti"

    @staticmethod
    def all():
        return list(set(BuildSpeed.id_to_buildspeed))

    @staticmethod
    def to_id(buildspeed):
        return BuildSpeed.id_to_buildspeed.index(buildspeed)

    @staticmethod
    def from_id(id):
        return BuildSpeed.id_to_buildspeed[id]

class CodeType():
    id_to_codetype = ["unknown"] * 0x4
    id_to_codetype[0x1] = "configuration"
    id_to_codetype[0x2] = "clear"
    id_to_codetype[0x3] = "setup"

    @staticmethod
    def all():
        return list(set(CodeType.id_to_codetype))

    @staticmethod
    def to_id(codetype):
        return CodeType.id_to_codetype.index(codetype)

    @staticmethod
    def from_id(id):
        return CodeType.id_to_codetype[id]

class SystemType():
    id_to_systemtype = ["unknown"] * 0x10
    id_to_systemtype[0x1] = "vantage"
    id_to_systemtype[0x2] = "vantage_b"
    id_to_systemtype[0x3] = "vantage_i_abs"
    id_to_systemtype[0x4] = "vantage_s"
    id_to_systemtype[0x5] = "vantage_se"
    id_to_systemtype[0x6] = "titan"
    id_to_systemtype[0x7] = "titan_hw"
    id_to_systemtype[0x8] = "titan_ti"
    id_to_systemtype[0x9] = "vantage_i_pc"
    id_to_systemtype[0xc] = "400mc"
    id_to_systemtype[0xe] = "900mc"
    id_to_systemtype[0xf] = "360mc"

    @staticmethod
    def all():
        return list(set(SystemType.id_to_systemtype))

    @staticmethod
    def to_id(systemtype):
        return SystemType.id_to_systemtype.index(systemtype)

    @staticmethod
    def from_id(id):
        return SystemType.id_to_systemtype[id]

class SetupcodeEncoder():
    dictionary = ['W','X','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','Y','J','K','L','M','N','Z','P','Q','R','S','T','U','V','W','X','Y','Z']
    magic_shift = [1, 3, 2, 5, 4, 3, 5, 2, 5, 4, 1, 3, 2, 5, 3, 4, 2, 1, 5]

    material_dict = [0, 30, 2, 24, 29, 1, 15, 22, 3, 31,26, 15, 22, 22, 7, 26, 16, 26, 14, 4,22, 4, 18, 7, 28, 5, 13, 14, 29, 27,27, 7, 22, 1, 1, 18, 18, 4, 20, 9,1, 21, 24, 16, 6, 30, 19, 24, 22, 18,25, 14, 2, 2, 15, 19, 9, 31, 16, 18,32, 5, 3, 8, 6, 18, 5, 4, 10, 14,20, 16, 16, 31, 18, 10, 19, 11, 23, 27,26, 3, 13, 11, 16, 7, 12, 26, 23, 27,1, 24, 27, 18, 10, 21, 13, 18, 13, 31,5, 12, 15, 3, 29, 31, 17, 26, 3, 7,12, 2, 6, 2, 30, 23, 6, 1, 1, 20,31, 15, 20, 20, 6, 29, 2, 30, 7, 9,27, 4, 18, 6, 25, 5, 15, 4, 11, 15,29, 8, 28, 7, 20, 18, 10, 3, 16, 18,27, 1, 3, 20, 0, 23, 3, 15, 8, 21,28, 24, 23, 29, 29, 12, 28, 24, 10, 6,31, 5, 22, 16, 29, 22, 3, 6, 17, 22,2, 16, 6, 8, 20, 14, 1, 14, 2, 1,5, 12, 22, 17, 21, 8, 14, 8, 14, 29,2, 14, 30, 27, 3, 0, 7, 27, 13, 24,27, 12, 30, 25, 26, 30, 18, 19, 10, 13,28, 5, 26, 23, 15, 6, 3, 1, 13, 10,3, 13, 19, 19, 24, 15, 31, 29, 20, 23,30, 16, 7, 9, 25, 0, 8, 29, 11, 13,27, 30, 31, 4, 17, 7, 24, 14, 23, 6,15, 29, 27, 30, 12, 11, 6, 10, 10, 18,13, 27, 20, 16, 28, 26, 20, 15, 13, 0,19, 29, 11, 8, 13, 7, 31, 15, 21, 25,27, 8, 19, 22, 4, 24, 12, 5, 20, 20,17, 6, 30, 29, 13, 20, 30, 24, 24, 1,30, 10, 23, 19, 17, 17, 22, 8, 15, 8,22, 14, 20, 3, 1, 28, 27, 7, 19, 25,3, 14, 0, 14, 10, 31, 15, 12, 7, 27,11, 24, 24, 12, 10, 21, 29, 10, 18, 17,0, 22, 16, 11, 20, 7, 30, 2, 26, 6,11, 0, 20, 6, 13, 11, 8, 22, 10, 9,1, 25, 26, 25, 4, 27, 15, 1, 18, 9,17, 1, 9, 0, 14, 3, 7, 8, 5, 0,8, 27, 21, 24, 7, 8, 23, 1, 1, 17,29, 4, 0, 11, 4, 29, 9, 19, 8, 6,16, 2, 20, 21, 11, 27, 7, 27, 2, 1,3, 30, 5, 17, 17, 6, 13, 26, 6, 15,5, 16, 25, 27, 20, 15, 9, 13, 9, 24,26, 12, 22, 7, 8, 18, 18, 1, 4, 12,20, 26, 27, 4, 31, 21, 14, 21, 29, 20,22, 23, 8, 6, 11, 12, 23, 28, 25, 3,22, 31, 5, 22, 25, 13, 3, 14, 10, 17,13, 16, 17, 21, 19, 24, 9, 27, 2, 15,10, 16, 0, 5, 22, 16, 11, 0, 16, 26,7, 17, 10, 4, 17, 7, 15, 24, 10, 29,30, 3];
    envelope_size_dict = [0,24,5]
    code_type_dict = [4,6,3,7]
    system_type_dict = [2,8,4,1,6,0,9,7,5,3,11,10,0,12,14,13]
    build_speed_dict = [0,13,27]
    sn0_dict = [7,6,4,5,1,8,10,9,3,2]
    sn1_dict = [9,10,8,6,2,5,7,4,1,3]
    sn2_dict = [2,7,3,8,6,10,4,5,9,1]
    sn3_dict = [6,2,7,1,4,9,8,10,3,5]
    sn_modulo = [3,8,9,1,7,0,2,5,4,6]
    mod_zero_dict = [21,14,3,7,0,11,13,22,17,0,15,19,7,5,0,20,10,4,12]
    mod_one_dict = [11,3,27,17,0,13,12,23,4,0,18,14,22,20,0,21,12,24,16]
    mod_two_dict = [25,12,14,4,0,1,17,11,19,0,24,21,23,31,0,22,15,23,12]
    mod_three_dict = [15,16,1,25,0,18,16,30,20,0,19,3,8,29,0,13,21,17,18]
    mod_four_dict = [9,11,17,29,0,19,18,31,3,0,21,27,17,9,0,12,22,4,9]
    mod_five_dict = [30,3,25,12,0,27,21,22,31,0,20,14,17,21,0,18,11,19,5]
    mod_six_dict = [29,5,2,19,0,26,31,15,12,0,17,1,25,30,0,16,31,20,28]
    mod_seven_dict = [17,15,21,2,0,22,9,10,4,0,11,17,6,8,0,18,16,23,29]
    mod_eight_dict = [23,18,11,22,0,16,21,14,24,0,3,15,12,25,0,5,10,14,20]
    mod_nine_dict = [3,24,12,25,0,14,22,4,23,0,13,14,4,21,0,17,11,10,16]

    def _randomize_code(self, serial_number):
        serial_code = [0] * 19

        mod_dict = []
        if (serial_number % 10 == 0x00):
            mod_dict = self.mod_zero_dict
        elif (serial_number % 10 == 0x01):
            mod_dict = self.mod_one_dict
        elif (serial_number % 10 == 0x02):
            mod_dict = self.mod_two_dict
        elif (serial_number % 10 == 0x03):
            mod_dict = self.mod_three_dict
        elif (serial_number % 10 == 0x04):
            mod_dict = self.mod_four_dict
        elif (serial_number % 10 == 0x05):
            mod_dict = self.mod_five_dict
        elif (serial_number % 10 == 0x06):
            mod_dict = self.mod_six_dict
        elif (serial_number % 10 == 0x07):
            mod_dict = self.mod_seven_dict
        elif (serial_number % 10 == 0x08):
            mod_dict = self.mod_eight_dict
        elif (serial_number % 10 == 0x09):
            mod_dict = self.mod_nine_dict

        for i in range(19):
            serial_code[i] = self.dictionary[mod_dict[i]]

        for i in [4,9,14]:
            serial_code[i] = '-'

        return serial_code

    def encode(self, serial_number, system_type, envelope_size, build_speed, material, code_type, version, key):
        output_code = ["\x00"] * 19

        seed_code = self._randomize_code(int(serial_number))

        material_id = self._material_id_from_names(material)
        (m_abs, m_ppsf, m_iso, mat) = self._encode_material(material_id)
        print("Debugging values:")
        print("\tmaterial id: %d" % material_id)
        print("\tabs: %d\n\tppsf: %d\n\tiso: %d\n\tmat: %d\n" % (m_abs, m_ppsf, m_iso, mat))

        if code_type == "configuration":
            # sn 1
            output_code[0] = self._encode_param(seed_code[0], int(serial_number[0]), 0x1F)
            # system type
            output_code[1] = self._encode_param(seed_code[1], SystemType.to_id(system_type) & 0x1F, 0x0F)
            # envelope size
            output_code[2] = self._encode_param(seed_code[2], EnvelopeSize.to_id(envelope_size) & 0x1F, 0x03)
            # build speed
            output_code[3] = self._encode_param(seed_code[3], BuildSpeed.to_id(build_speed) & 0x1F, 0x03)
            output_code[4] = "-"
            # material (abs)
            output_code[5] = self._encode_param(seed_code[5], int(m_abs) & 0x1F, 0x1F)
            # sn 2
            output_code[6] = self._encode_param(seed_code[6], int(serial_number[1]), 0x1F)
            # checksum 1
            #output_code[7]
            # checksum 2
            #output_code[8]
            output_code[9] = "-"
            # material (ppsf)
            output_code[10] = self._encode_param(seed_code[10], int(m_ppsf) & 0x1F, 0x1F)
            # material (iso)
            output_code[11] = self._encode_param(seed_code[11], int(m_iso) & 0x1F, 0x1F)
            # sn 3
            output_code[12] = self._encode_param(seed_code[12], int(serial_number[2]), 0x1F)
            # version
            output_code[13] = self._encode_param(seed_code[13], int(version) & 0x1F, 0x03)
            output_code[14] = "-"
            # code type
            output_code[15] = self._encode_param(seed_code[15], CodeType.to_id(code_type) & 0x1F, 0x03)
            # material
            output_code[16] = self._encode_param(seed_code[16], int(mat) & 0x1F, 0x1F)
            # key
            #output_code[17]
            # sn4
            output_code[18] = self._encode_param(seed_code[18], int(serial_number[3]), 0x1F)
        elif code_type == "clear":
            pass
        elif code_type == "setup":
            pass
        else:
            raise(Exception("invalid code_type <" + code_type + ">"))

        checksum = self._checksum_compose(output_code)
        output_code[7] = self.dictionary[self._do_shift(0, (checksum >> 4) & 0xF)]
        output_code[8] = self.dictionary[self._do_shift(0, checksum & 0xF)]

        setup_code = self._shift_code(output_code,
                serial_number,
                SystemType.to_id(system_type),
                EnvelopeSize.to_id(envelope_size),
                BuildSpeed.to_id(build_speed),
                int(material_id),
                CodeType.to_id(code_type),
                key)

        print("Generated code:")
        print("\t" + "".join(setup_code))

    def decode(self, setup_code):
        try:
            code = self._unshift_code(setup_code)
        except Exception as exc:
            raise(Exception("invalid code"))

        expected_checksum = 16 * code[7] + code[8]
        checksum = self._checksum(code)

        if expected_checksum != checksum:
            raise(Exception("invalid checksum, expected <" + str(expected_checksum) + "> but computed <" + str(checksum) + ">"))

        code_type = (code[13] & 0x03)
        if code_type not in (0x0, 0x01, 0x02, 0x03):
            raise(Exception("invalid code type < " + str(hex(code[13] & 0x03)) + ">"))

        s = Setupcode()
        s.serial_number = "".join(str(c) for c in [code[0], code[6], code[12], code[18]])
        s.system_type = SystemType.from_id(int(code[1] & 0x0F))
        s.envelope_size = EnvelopeSize.from_id(code[2] & 0x03)
        s.build_speed = BuildSpeed.from_id(code[3] & 0x03)
        s.checksum_1 = str(code[7])
        s.checksum_2 = str(code[8])
        s.version = str(code[13] & 0x03)
        s.material = self._get_enabled_material(self._decode_material(code)) + "(" + str(self._decode_material(code)) + ")"
        s.code_type = CodeType.from_id(code[15] & 0x03)
        s.key = str(self.dictionary.index(setup_code[17]))

        print("Debugging values:")
        print("\tmaterial id: %d" % self._decode_material(code))
        print("\tabs: %d\n\tppsf: %d\n\tiso: %d\n\tmat: %d\n" % (code[5], code[10], code[11], code[16]))

        return s

    def _get_enabled_material(self, material):
        supported_material = ""
        counter = 0
        i=1

        while i <= 256:
            if material & i:
                supported_material += CodeMaterial.from_id(counter) + " "
            i *= 2
            counter+=1

        # Another version found:

        #if material & 0x01 or material & 0x02 or material & 0x04:
        #    mat_name = "ABS "
        #if material & 0x08 or material & 0x10:
        #    mat_name = "ABS-PC "
        #if material & 0x20 or material & 0x40:
        #    mat_name = "PC "
        #if material & 0x80 or material & 0x100:
        #    mat_name = "PPSF "
        #if material & 0x200:
        #    mat_name = "ISO "

        return supported_material

    def _material_id_from_names(self, material_names):
        material_id = 0

        for material_name in material_names:
            material_id |= (1 << CodeMaterial.to_id(material_name))

        return material_id

    def _encode_material(self, material):
        mat_abs = material & 0x01
        mat_abs |= material & 0x02
        mat_abs |= material & 0x04
        mat_abs |= material & 0x08
        if material & 0x200:
            mat_abs |= 0x10

        mat_ppsf = 0
        if material & 0x10:
            mat_ppsf |= 0x01
        if material & 0x20:
            mat_ppsf |= 0x02
        if material & 0x40:
            mat_ppsf |= 0x04
        if material & 0x80:
            mat_ppsf |= 0x08
        if material & 0x100:
            mat_ppsf |= 0x10

        mat_iso = 0
        if material & 0x400:
            mat_iso |= 0x01
        if material & 0x800:
            mat_iso |= 0x02
        if material & 0x1000:
            mat_iso |= 0x04
        if material & 0x2000:
            mat_iso |= 0x08
        if material & 0x4000:
            mat_iso |= 0x10

        mat = 0
        if material & 0x8000:
            mat |= 0x01
        if material & 0x10000:
            mat |= 0x02
        if material & 0x20000:
            mat |= 0x04
        if material & 0x40000:
            mat |= 0x08
        if material & 0x80000:
            mat |= 0x10

        return (mat_abs, mat_ppsf, mat_iso, mat)

    def _encode_param(self, code, value, notv):
        return self.dictionary[(~notv & self._dict_get_position(code) & 0x1F) | value]

    def _shift_code(self, setup_code, serial_number, system_type, envelope_size, build_speed, material, code_type, key):
        # Get the shift base value

        # Algorithm 1
        #shift_base = self.build_speed_dict[build_speed] & 0xff
        #shift_base = (shift_base + self.material_dict[material%0x100000]) & 0xff
        #shift_base = (shift_base + self.envelope_size_dict[envelope_size]) & 0xff
        #shift_base = (shift_base + self.code_type_dict[code_type]) & 0xfF
        #shift_base = (shift_base + self.system_type_dict[system_type]) & 0xff
        #shift_base = (shift_base + self._unnormalize_sn(serial_number, code_type)) & 0xff

        # Algorithm 2
        #shift_base = self.code_type_dict[code_type] + self.system_type_dict[system_type]  + self._unnormalize_sn(serial_number, code_type)

        # Algorithm 3
        shift_base = self.build_speed_dict[build_speed] & 0xff
        shift_base = (shift_base + self.material_dict[material & 0x1ff])
        shift_base = (shift_base + self.envelope_size_dict[envelope_size]) & 0xff
        shift_base = (shift_base + self.code_type_dict[code_type]) & 0xfF
        shift_base = (shift_base + self.system_type_dict[system_type]) & 0xff
        shift_base = (shift_base + self._unnormalize_sn(serial_number, code_type)) & 0xff

        if int(serial_number) & 1:
            shift_base += 4

        if key != 0:
            shift_base = key

        error = 0
        while shift_base > 0x1f:
            shift_base = (shift_base - 0x20) & 0xff
            error = error + 1
            if error > 5 :
                raise "error > 5 :("

        for i in [0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 18]:
            position = self._dict_get_position(setup_code[i])
            shift = self._do_shift(position, shift_base + self.magic_shift[i])
            setup_code[i] = self.dictionary[shift]

        setup_code[17] = self.dictionary[self._do_shift(0, shift_base)]

        return setup_code

    def _unshift_code(self, input_code):
        new_code = [0x00] * 19
        base_shift = self.dictionary.index(input_code[17])

        for i in [0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18]:
            position = self._dict_get_position(input_code[i])
            new_code[i] = self._do_unshift(position, base_shift + self.magic_shift[i])

        for i in [4, 9, 14]:
            new_code[i] = "-"

        return new_code

    def _do_shift(self, position, value):
        if value > 0x20:
            value = (value % 10) & 0xFF
        output = (value + position) & 0xFF
        if output > 0x1F:
            output = (output - 0x20) & 0xFF
        return output

    def _do_unshift(self, base_shift, value):
        if value > 0x20:
            value = value % 10
        value_2 = 0
        if base_shift - value < 0:
            value_2 = 0x20

        return (base_shift - value + value_2) & 0xff

    def _checksum(self, code):
        checksum = 0
        for i in [0, 1, 2, 3, 5, 6, 10, 11, 12, 13, 15, 16, 18]:
            checksum += code[i] & 0xffff
        return checksum

    def _checksum_compose(self, code):
        checksum = 0
        for i in [0, 1, 2, 3, 5, 6, 10, 11, 12, 13, 15, 16, 18]:
            checksum += self._dict_get_position(code[i])
        return checksum

    def _decode_material(self, code):
        material = ((code[5] & 0x01) + (code[5] & 0x02) + (code[5] & 0x04) + (code[5] & 0x08))
        if code[5] & 0x10:
            material |= 0x200

        material |= ((code[10] & 0x1) + (code[10] & 0x02) + (code[10] & 0x04) + (code[10] & 0x08) + (code[10] & 0x10)) << 0x04

        if (code[13] & 0x03) > 1:
            if code[11] & 0x01:
                material |= 0x400
            if code[11] & 0x02:
                material |= 0x800
            if code[11] & 0x04:
                material |= 0x1000
            if code[11] & 0x08:
                material |= 0x2000
            if code[11] & 0x10:
                material |= 0x4000

            if code[16] & 0x01:
                material |= 0x8000
            if code[16] & 0x02:
                material |= 0x10000
            if code[16] & 0x04:
                material |= 0x20000
            if code[16] & 0x08:
                material |= 0x40000
            if code[16] & 0x10:
                material |= 0x80000

        return material

    def _dict_get_position(self, value):
        try:
            position = self.dictionary.index(value)
            if position > 31:
                position = 31
        except:
            position = 31

        return position

    def _unnormalize_sn(self, sn, code_type):
        sn_length = len(sn.lstrip("0"))

        value = 0
        if code_type == 3:
            if sn_length == 1:
                # 000#
                value = self.sn3_dict[int(sn[3])]
            elif sn_length == 2:
                # 00#0
                value = self.sn2_dict[int(sn[2])] + self.sn3_dict[int(sn[3])]
            elif sn_length == 3:
                # 0#00
                value = self.sn1_dict[int(sn[1])] + self.sn2_dict[int(sn[2])] + self.sn3_dict[int(sn[3])]
            elif sn_length == 4:
                # #000
                value = self.sn0_dict[int(sn[0])] + self.sn1_dict[int(sn[1])] + self.sn2_dict[int(sn[2])] + self.sn3_dict[int(sn[3])]
        else:
            if sn_length == 1:
                # 000#
                value = self.sn3_dict[int(sn[3])]
            elif sn_length == 2:
                # 00#0
                value = self.sn2_dict[int(sn[2])] + self.sn3_dict[int(sn[3])]
            elif sn_length == 3:
                # 0#00
                value = self.sn1_dict[int(sn[1])] + self.sn2_dict[int(sn[2])] + self.sn3_dict[int(sn[3])]
            elif sn_length == 4:
                # #000
                value = self.sn0_dict[int(sn[0])] + self.sn1_dict[int(sn[1])] + self.sn2_dict[int(sn[2])] + self.sn3_dict[int(sn[3])]

        if value % 10 <= 9:
            value += self.sn_modulo[value%10]

        return value

