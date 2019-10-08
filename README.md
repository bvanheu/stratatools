[![Build Status](https://travis-ci.org/bvanheu/stratatools.svg?branch=master)](https://travis-ci.org/bvanheu/stratatools)

Stratatools
-----------

This is software to read and write data on a Stratasys cartridge EEPROM.

You can use this code to 'refill' an EEPROM or build a cartridge EEPROM image
from scratch.

## Installation

This tool requires Python 2.7.

You can simply installs Stratatools using pip:

```
$ pip2 install stratatools
```

or from source:

```
$ python2 ./setup.py build
$ python2 ./setup.py install
```

It will automagically pull the dependency:

- [pycryptodome](https://www.pycryptodome.org)
- [pyserial](https://github.com/pyserial/pyserial/)
- [protobuf](https://github.com/google/protobuf/tree/master/python)
- [pyudev](https://github.com/pyudev/pyudev)

## Cartridge Usage

### Print information about a cartridge

You have to provide the machine type (fox, prodigy, quantum, etc.) and the
EEPROM uid, in hexadecimal form without the '0x' prefix. Note that the EEPROM
uid to use ends with "23" (which is the family code for the EEPROM device).

```
$ stratatools eeprom_decode \
    --machine-type fox \
    --eeprom-uid 2362474d0100006b \
    cartridge_dump.bin
```

The EEPROM uid should starts with the family code, something like '23' or 'b3'.
It is then followed by a 6 bytes id then finish with a checksum.

On Linux, it is the content of the `id` pseudo file.

If you provide the '-D' option, the input file will be interpreted as an ASCII
formatted file, containing lines of the form produced by the printers 'er'
command, namely:

```
000096: 00 00 00 00 00 00 00 00 53 54 52 41 54 41 53 59   ........STRATASY
```

Otherwise, the input file must be a binary file.

### Create your own cartridge

By providing all the required information, this software will provide a new
valid EEPROM image that you can write to a cartridge.

First, create a new EEPROM proto using the `eeprom_create` command.

You can customize any parameters in the following example:

```
$ stratatools eeprom_create \
    --serial-number 1234.0 \
    --material-name ABS \
    --manufacturing-lot 1234 \
    --manufacturing-date "2001-01-01 01:01:01" \
    --use-date "2002-02-02 02:02:02" \
    --initial-material 11.1 \
    --current-material 22.2 \
    --key-fragment 4141414141414141 \
    --version 1 \
    --signature STRATASYS > cartridge.txt
```

Alternatively, create a text file `cartridge.txt` with the following content:
```
serial_number: 1234.0
material_name: "ABS"
manufacturing_lot: "1234"
manufacturing_date {
  seconds: 1436540129
}
last_use_date {
  seconds: 1436540129
}
initial_material_quantity: 42.0
current_material_quantity: 42.0
key_fragment: "4141414141414141"
version: 1
signature: "STRATASYS"
```

All the dates are in international format: `yyyy-mm-dd hh:mm:ss`.

You can then use `eeprom_encode` to create the binary file used by the printer.

```
$ stratatools eeprom_encode \
    --machine-type fox \
    --eeprom-uid 2362474d0100006b \
    cartridge.txt cartridge.bin
```

You have to provide the correct machine-type and the valid eeprom uid.

The EEPROM uid should starts with the family code, something like '23' or 'b3'.
It is then followed by a 6 bytes id then finish with a checksum.

The generated file will be 113 bytes in size. You can complete the file with
zeroes if you want to make it 512 bytes long, the usual EEPROM size.

Supplying the '-D' option will result in an output file containing a
double-quoted string of space delimited bytes, expressed in hexadecimal.

Otherwise, the output will be a binary file.

You can also pipe the two commands together:

```
$ stratatools eeprom_create \
    --serial-number 1234.0 \
    --material-name ABS \
    --manufacturing-lot 1234 \
    --manufacturing-date "2001-01-01 01:01:01" \
    --use-date "2002-02-02 02:02:02" \
    --initial-material 11.1 \
    --current-material 22.2 \
    --key-fragment 4141414141414141 \
    --version 1 \
    --signature STRATASYS | \
    stratatools eeprom_encode -t fox -e 2362474d0100006b > cartridge.bin
```

### List supported material

If you want a list of all known material, simply run the following:

```
$ stratatools material --list
0       ABS
1       ABS_RED
2       ABS_GRN
[...]
```

Use those names when creating a new cartridge.

### Errors

If you have an `invalid checksum` error, the code was not able to decrypt your
EEPROM correctly. Verify that your EEPROM file is valid, double check the
EEPROM uid.

If it still doesn't work, fill a ticket on Github.

### Automation with a Raspberry Pi

A helper script is available if you wish to automatically rewrite cartridges
using a Raspberry Pi. The script will set the manufacturing date to 'today'.
It will also randomize the serial number and set the current material qty to
the initial material quantity.

You will need a working 1wire setup on the Raspberry Pi, see below on how to
do that.

To simply refill a cartridge, launch the helper script specifying the printer
type:

```
$ stratatools_rpi_daemon prodigy
```

You can also provide a cartridge template:
```
$ stratatools_rpi_daemon --template ./abs_cartridge.txt prodigy
```


## Configuration Code

This script is able to generate configuration code for your printer. There are
actually 3 different codes available:

* configuration
* setup
* clear

We're only able to generate `configuration` code for now. These codes can
unlock specific features of your printer.

### Information about a configuration code

To decode a configuration code, simply run the following:

```
$ stratatools setupcode_decode AAAA-BBBB-CCCC-DDDD
```

### Create your own configuration code

You can create your own configuration code to enable specific features.

For example:

```
$ stratatools setupcode_create \
    --serial-number 1234 \
    --system-type 900mc \
    --type configuration \
    --envelope-size large \
    --build-speed 1x \
    --material ABS-M30 NYLON PC-ABS \
    --version 1
```

Will generate a `configuration` code for a printer type 900mc.

For help on available values, you can run the following:

```
$ stratatools setupcode_create --help
```

## Interesting fork / rewrite

* [slaytonrd/CartridgeWriter](https://github.com/slaytonrnd/CartridgeWriter) - rewritten in C# by slaytonrd
* [mayrthom/CartridgeWriter_uPrint](https://github.com/mayrthom/CartridgeWriter_uPrint) - rewrite of the CartridgeWriter, that works with the uPrint


## Interfacing with the cartridge

### Bus-pirate

- Use the MISO wire (orange) for the data
- Use the GROUND wire (black) on the ground
- Connect the 5V (grey) on the pull-up voltage input (blue)

Use the following schematic as a reference:

```
Bus pirate

    grey    >---+
                | (connected together)
    blue    >---+

                 eeprom
                +------+
    orange  >---| Data |
                |      |
    black   >---| Gnd  |
                +------+
```

Two helper scripts are available to interact with the BusPirate.

To read an eeprom:

```
$ stratatools_bp_read /dev/ttyUSB0 eeprom.bin
```

To write an eeprom:

```
$ stratatools_bp_write /dev/ttyUSB0 eeprom_new.bin
```

### Raspberry Pi

- Use the GPIO 4 (pin 7) for the data
- Use any GROUND (pin 6,9,14,20 or 25) on the ground
- Use the 5V Power (pin 2) to pull-up the data line using a ~4.7k resistor

Use the following schematic as a reference:

```
Raspberry pi

     5V     >---+
                |
           4.7k Z    eeprom
                |   +------+
    GPIO4   >---+---| Data |
                    |      |
    GROUND  >-------| Gnd  |
                    +------+
```

Then you'll need to probe 2 kernel modules:

```
$ sudo modprobe w1-gpio gpiopin=4
$ sudo modprobe w1-ds2433
```

You might need to change the device-tree overlay. Update the following file
`/boot/config.txt`, and add this line at the end:

```
dtoverlay=w1-gpio,gpiopin=4
```

If detection is slow on the bus, you can try to reduce the timeout. Create
the following file `/etc/modprobe.d/wire.conf` with the following:

```
options wire timeout=1 slave_ttl=3
```

You should now see your eeprom appearing:

```
$ ls -l /sys/bus/w1/devices/w1_bus_master1
23-xxxxxxxxxxxx/
[...]
```

To print the eeprom uid:

```
$ xxd -p /sys/bus/w1/devices/w1_bus_master1/23-xxxxxxxxxxxx/id
23xxxxxxxxxxxx
```

To read an eeprom:

```
$ cp /sys/bus/w1/devices/w1_bus_master1/23-xxxxxxxxxxxx/eeprom ~/eeprom.bin
```

To write an eeprom:

```
$ cp ~/eeprom_new.bin /sys/bus/w1/devices/w1_bus_master1/23-xxxxxxxxxxxx/eeprom
```

#### DS2432

To interface with a DS2432, you'll need to follow the steps found in this
project: https://github.com/bvanheu/ds2432-linux .

## Acknowledgement

Special thanks to the Stratahackers group. Without them, nothing like this
could be possible. They provided moral and technical support!

Thanks to ashanin for the uPrint support.
Thanks to ajtayh for ASA and ULT1010 in setupcode.
