Stratasys
---------

This is a software to read and write data on a Stratasys cartridge memory.

You may want to use it so you can refill or build your own cartridge.

## Installation

### Dependencies

- python 2.7
- [pycrypto](https://www.dlitz.net/software/pycrypto/)

## Usage

### Print information about a cartridge

You have to provide the machine type (fox, prodigy or quantum) and the EEPROM uid,
in hexadecimal form without the '0x' prefix.

    $ ./stratasys-cli.py info -t fox -e 4141414141414141 -i eeprom.bin -u -r
    Cartridge
    ---------
    Serial number           1234.0
    Material                ABS (0 - 0x0)
    Manufacturing lot       1234
    Manufacturing date      2001-01-01 01:01:01
    Last use date           2002-02-02 02:02:02
    Initial quantity        11.1
    Current quantity        22.2
    Key fragment            4141414141414141
    Version                 1
    Signature               STRATASYS
    ---------
    To recreate the provided cartridge:
    --machine-type fox --eeprom-uid 4343434343434343 --serial-number 1234.0 --material-name ABS --manufacturing-lot 1234 --manufacturing-date "2001-01-01 01:01:01" --use-date "2002-02-02 02:02:02" --initial-material 11.1 --current-material 22.2 --key-fragment 4141414141414141 --version 1 --signature STRATASYS

If you provide the '-h' option, the information printed will be human readable.

If you provide the '-r' option, the arguments will be printed if you want to recreate
the cartridge.

### Create your own cartridge

By providing all required information, the software will provide a new valid eeprom
that you can write on a cartridge.

    ./stratasys-cli.py create --machine-type fox --eeprom-uid 4343434343434343 --serial-number 1234.0 --material-name ABS --manufacturing-lot 1234 --manufacturing-date "2001-01-01 01:01:01" --use-date "2002-02-02 02:02:02" --initial-material 11.1 --current-material 22.2 --key-fragment 4141414141414141 --version 1 --signature STRATASYS -o test_recreate.bin

All the dates are in international format: yyyy-mm-dd hh:mm:ss

You have to provide the correct machine-type and the valid eeprom uid. You can
customize all the rest.

## Acknowledgement

Special thanks to the Stratahackers group. Without them, nothing like this could
be possible. They provided moral and technical support!
