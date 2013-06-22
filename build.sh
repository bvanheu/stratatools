#!/bin/sh

rm bin/stratasys
gcc -Wall src/des.c src/crypto.c src/stratasys.c -o bin/stratasys
