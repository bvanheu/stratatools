Stratasys
---------

This is a software to read and write data on a Stratasys canister memory, Fortus model.

## Use case

You may want to use that software so you can refill your own canister, build your own canister, etc.

## How do i compile 'stratasys'?

Simply run:
    $ ./build.sh

The binary will be in 'bin/stratasys'

## Tools

### bin/parse_binary.py

This python script read a decrypted configuration to a human readable format.

	$ ./bin/parse_binary.py test.bin
	Canister S/N: <serial number>
	Material type: <material>
	Manufacturing lot: <mfg lot>
	Manufacturing date: <mfg date>
	Use date: <last use date>
	Initial material qty: <quantity of material>
	Current material qty: <remaining material>
	Key: <configuration key>

### bin/create_binary.py

This python script is used to create a binary that can be encrypted then flashed on a canister.

	$ ./bin/create_binary.py --help
	-s : canister serial number
	-t : material type (see the list in the file create_binary.py)
	-d : creation date
	-u : last use date
	-i : initial material quantity
	-c : remaining material quantity
	-k : key to crypt/decrypt this configuration file
	-o : output file

    $ ./create_binary.py -s 123456789.0 -t PC-ABS -l 1234 -d "2013-09-28 01:02:03" -u "2013-09-29 01:02:03" -i 92.3 -c 91.6059082031 -k 123456789abcdef0 -o canister.bin

### bin/stratasys

This binary is used to crypt/decrypt a binary. Note that the file must be in binary form and note in hex representation. You may hack the file 'bin/dump_binary.py' in order to make the conversion. The final file should be 512 bytes.

	$ ./bin/stratasys --help
	-e or -d: encrypt or decrypt
	-m : printer model number
	-u : EEPROM canister serial number
	-i : input file
	-o : output file

    $ ./bin/stratasys -e -m 123456789abcdef0 -u 123456789abcdef0 -i ./canister.bin -o ./crypted_canister.bin

