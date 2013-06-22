This is a software to read and write data on a Stratasys canister memory.

## Use case

You may want to use that software so you can refill your own canister, build your own canister, etc.

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

	$ ./create_binary.py -s <serial number> -t <material type> -l <mfg lot> -d <mfg date> -u <last use date> -i <initial quantity of material> -c <remaining material quantity> -k <configuration key> -o <output file>

	$ ./create_binary.py --help
	-s : canister serial number
	-t : material type (see the list in the file create_binary.py)
	-d : creation date
	-u : last use date
	-i : initial material quantity
	-c : remaining material quantity
	-k : key to crypt/decrypt this configuration file
	-o : output file

### bin/stratasys

This binary is used to crypt/decrypt a binary.

	$ ./bin/stratasys -e -m <printer serial number> -u <canister S/N> -i <input file> -o <output file>
	$ ./bin/stratasys --help
	-e ou -d: encrypt or decrypt
	-m : printer model number
	-u : EEPROM canister serial number
	-i : input file
	-o : output file

## How do i compile 'stratasys'?

Simply run:
	$ ./build.sh

The binary will be in 'bin/stratasys'

