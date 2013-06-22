/*
 * Copyright (c) 2013, Benjamin Vanheuverzwijn <bvanheu@gmail.com>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of the <organization> nor the
 *       names of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <getopt.h>
#include <errno.h>

#include "crypto.h"

char prog_name[256];

enum mode {
    MODE_ENCRYPT,
    MODE_DECRYPT
};

struct stratasys_options {
    enum mode mode;
    char in_file[256];
    char out_file[256];
    uint8_t uid[8];
    uint8_t machine_number[8];
};

struct stratasys_options options;

void print_usage() {
    printf("usage: %s [-e|--encrypt or -d|--decrypt] -m|--machine-number <machine number> -u|--uid <eeprom uid> -i|--in <in path> -o|--out <out path>\n", prog_name);
    printf("\narguments:\n");
    printf("\t-e|--encrypt:\tEncrypt input file into output file\n");
    printf("\t-d|--decrypt:\tDecrypt input file into output file\n");
    printf("\t-m|--machine-number <machine number>:\tPrinter serial number\n");
    printf("\tKnown machine number:\n");
    printf("\t\t0x2C30478BB7DE81E8\n");
    printf("\t-u|--uid <eeprom uid>:\tEEPROM Unique IDentifier\n");
    printf("\t-i|--in <input path>:\tInput file\n");
    printf("\t-o|--out <output path>:\tOutput file\n");
}

void parse_arguments(int argc, char *argv[]) {
    int long_index = 0;
    int opt;
    struct option long_options[] =
    {
        {"help", no_argument, NULL, 'h'},
        {"encrypt", no_argument, NULL, 'e'},
        {"decrypt", no_argument, NULL, 'd'},
        {"in", required_argument, NULL, 'i'},
        {"out", required_argument, NULL, 'o'},
        {"machine_number", required_argument, NULL, 'm'},
        {"uid", required_argument, NULL, 'u'},
        {0, 0, 0, 0}
    };

    strncpy(prog_name, argv[0], 256);

    while ((opt = getopt_long(argc, argv, "hedi:o:u:m:", long_options, &long_index)) != -1) {
        switch (opt) {
            case 'e':
                options.mode = MODE_ENCRYPT;
                break;
            case 'd':
                options.mode = MODE_DECRYPT;
                break;
            case 'i':
                strncpy(options.in_file, optarg, 256);
                break;
            case 'o':
                strncpy(options.out_file, optarg, 256);
                break;
            case 'm':
                sscanf(optarg, "%2hhx%2hhx%2hhx%2hhx%2hhx%2hhx%2hhx%2hhx", &options.machine_number[0], &options.machine_number[1], &options.machine_number[2], &options.machine_number[3], &options.machine_number[4], &options.machine_number[5], &options.machine_number[6], &options.machine_number[7]);
                break;
            case 'u':
                sscanf(optarg, "%2hhx%2hhx%2hhx%2hhx%2hhx%2hhx%2hhx%2hhx", &options.uid[0], &options.uid[1], &options.uid[2], &options.uid[3], &options.uid[4], &options.uid[5], &options.uid[6], &options.uid[7]);
                break;
            case 'h':
                print_usage();
                exit(EXIT_SUCCESS);
                break;
            default:
                print_usage();
                exit(EXIT_FAILURE);
                break;
        }
    }

    if (strlen(options.in_file) == 0 || strlen(options.out_file) == 0) {
        printf("Error: please provide input file and output file\n");
        print_usage();
        exit(EXIT_FAILURE);
    }

    if (options.uid[0] == 0x00) {
        printf("Error: please provide EEPROM UID\n");
        print_usage();
        exit(EXIT_FAILURE);
    }

    if (options.machine_number[0] == 0x00) {
        printf("Error: please provide machine number\n");
        print_usage();
        exit(EXIT_FAILURE);
    }
}

int main(int argc, char *argv[]) {
    int fd;
    ssize_t bytes;
    uint8_t crypted_text[0x200] = {0};
    uint8_t plain_text[0x200] = {0};
    crypto_t *crypto;

    printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
    printf("Stratasys Cryptography Service\n");
    printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");

    parse_arguments(argc, argv);

    crypto = crypto_new();

    printf("EEPROM UID: %02hhX%02hhX%02hhX%02hhX%02hhX%02hhX%02hhX%02hhX\n", options.uid[0], options.uid[1], options.uid[2], options.uid[3], options.uid[4], options.uid[5], options.uid[6], options.uid[7]);
    printf("Machine number: %02hhX%02hhX%02hhX%02hhX%02hhX%02hhX%02hhX%02hhX\n", options.machine_number[0], options.machine_number[1], options.machine_number[2], options.machine_number[3], options.machine_number[4], options.machine_number[5], options.machine_number[6], options.machine_number[7]);

    if (options.mode == MODE_ENCRYPT) {
        printf("[+] Reading %s...", options.in_file);

        // Read plain text
        fd = open(options.in_file, O_RDONLY);
        if (fd < 0) {
            printf("Error: %s: %s\n", options.in_file, strerror(errno));
            exit(EXIT_FAILURE);
        }
        bytes = read(fd, plain_text, 0x68);
        close(fd);
        printf("%d bytes\n", bytes);

        // Encrypt stuff
        if (crypto_encrypt_canister(crypto, options.machine_number, options.uid, plain_text, crypted_text, 0x68)) {
            printf("Error ^\n");
            exit(EXIT_FAILURE);
        }

        // Write crypted text
        printf("[+] Writing %s...", options.out_file);
        fd = open(options.out_file, O_CREAT|O_WRONLY, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);
        bytes = write(fd, crypted_text, 0x68);
        close(fd);
        printf("\t%d bytes\n", bytes);
    }
    else {
        // Read plain text
        printf("[+] Reading %s ... ", options.in_file);
        fd = open(options.in_file, O_RDONLY);
        if (fd < 0) {
            printf("Error: %s: %s\n", options.in_file, strerror(errno));
            exit(EXIT_FAILURE);
        }
        bytes = read(fd, crypted_text, 0x68);
        close(fd);
        printf("%d bytes\n", bytes);

        // Decrypt stuff
        if (crypto_decrypt_canister(crypto, options.machine_number, options.uid, crypted_text, plain_text, 0x68)) {
            printf("Error ^\n");
            exit(EXIT_FAILURE);
        }

        // Write crypted text
        printf("[+] Writing %s...", options.out_file);
        fd = open(options.out_file, O_CREAT|O_WRONLY, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);
        bytes = write(fd, plain_text, 0x68);
        close(fd);
        printf("%d bytes\n", bytes);
    }

    return EXIT_SUCCESS;
}
