import unittest
from stratatools import checksum

class TestCrc16(unittest.TestCase):
    def test_checksum(self):
        expected_crc16 = 14743

        crc = checksum.Crc16_Checksum()
        crc16 = crc.checksum(bytearray("abcd"))

        assert expected_crc16 == crc16
