#
# See the LICENSE file
#
import re
import binascii

class Formatter:
    def __init__(self):
        pass

    def from_source(self, data):
        raise Exception("this class cannot be used")

    def to_destination(self, data):
        raise Exception("this class cannot be used")

class DiagnosticPort_Formatter(Formatter):
    def __init__(self):
        self.rx = re.compile('^[0-9]{6}: ((?:[0-9a-f-A-F]{2} ?)+).*?$',re.MULTILINE)

    def from_source(self, data):
        formatted = b''
        idx = 1
        for match in self.rx.finditer(data):
            try:
                #Get a line of data with whitespace removed
                line = match.group(1).replace(' ', '')
                formatted += binascii.unhexlify(line)
                idx=idx+1
            except IndexError:
                print("Error on line %s when reading diag port formatted data" % (idx,))
                raise

        return formatted

    def to_destination(self, data):
        formatted = "\""

        for b in data:
            formatted += binascii.hexlify(b) + " "

        return formatted[0:-1] + "\""
