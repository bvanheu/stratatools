#
# See the LICENSE file
#

class Formatter:
    def __init__(self):
        pass

    def from_source(self, data):
        raise Exception("this class cannot be used")

    def to_destination(self, data):
        raise Exception("this class cannot be used")

class DiagnosticPort_Formatter(Formatter):
    def __init__(self):
        pass

    def from_source(self, data):
        formatted = ""

        # TODO - implements me

        return formatted

    def to_destination(self, data):
        formatted = ""

        for b in data:
            formatted += binascii.hexlify(b) + ", "

        return formatted[0:-2]
