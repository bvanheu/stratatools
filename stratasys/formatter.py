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

#Reads a series of newline delimited lines of the format:
#000096: 00 00 00 00 00 00 00 00 53 54 52 41 54 41 53 59   ........STRATASY

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

#Produces a double-quoted, space separated string suitable for providing to the uPrint's 'ew' diagnostic command
    def to_destination(self, data):
        formatted = "\""

        for b in data:
            formatted += binascii.hexlify(chr(b)) + " "

        return formatted[0:-1] + "\""
