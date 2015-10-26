#
# See the LICENSE file
#

#
# A machine is a printer from stratasys
#
type_to_number = {
    "fox": "2C30478BB7DE81E8",
    "fox2": "2C30479BB7DE81E8",
    "ktype": "6B2A268B5ED3374A",
    "prodigy": "5394D7657CED641D",
    "quantum": "76C454D532E610F7",
    "uprint": "F3A91DBE6B0B2255",
    "uprintse": "6B2A268B5ED3374A",
}

number_to_type = {}

def get_number_from_type(type):
    return type_to_number[type]

def get_type_from_number(number):
    if len(number_to_type) == 0:
        for key, value in enumerate(type_to_number):
            number_to_type[value] = key

    return number_to_type[number]
