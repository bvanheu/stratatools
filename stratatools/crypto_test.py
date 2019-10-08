import unittest
from stratatools.crypto import Desx_Crypto

DESX_KEY = bytearray(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f")

class TestCrypto(unittest.TestCase):
    def test_desx_encrypt(self):
        expected_ciphertext = bytearray(b"\x38\xdb\x9b\xe0\x9d\x1b\x24\xa0\x7c\x77\x49\x26\xaf\x94\xe8\xd5")

        desx = Desx_Crypto()

        ciphertext = desx.encrypt(DESX_KEY, "this is a test..")

        assert expected_ciphertext == ciphertext

    def test_desx_encrypt_decrypt(self):
        expected_plaintext = "this is a test.."

        desx = Desx_Crypto()

        plaintext = desx.decrypt(DESX_KEY, desx.encrypt(DESX_KEY, expected_plaintext))

        assert expected_plaintext == plaintext
