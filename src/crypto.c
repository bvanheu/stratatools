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

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>

#include "des.h"
#include "crypto.h"

int encryption_len[] = {0x8, 0x8, 0x14, 0x8,  0x8,  0x8,  0x2,  0x2,  0x8,  0x2,  0x2 , 0x8 , 0x2 , 0x2,  0x48, 0x10, 0x10};
int encryption_map[] = {0x0, 0x8, 0x10, 0x28, 0x30, 0x38, 0x40, 0x46, 0x48, 0x50, 0x24, 0x58, 0x60, 0x62, 0x0,  0x58, 0x48};
enum encryption_map_name {
    ENC_CANISTER_SN = 0,
    ENC_MATERIAL_TYPE = 1,
    ENC_MFG_LOT = 2,
    ENC_MFG_DATE = 3,
    ENC_USE_DATE = 4,
    ENC_INIT_MAT_QTY = 5,
    ENC_PLAINTEXT_CRC = 6,
    ENC_UNK_CRC =7,
    ENC_UNK = 8,
    ENC_UNK_CRC2 = 9,
    ENC_UNK_CRC3 = 10,
    ENC_CUR_MAT_QTY = 11,
    ENC_CUR_MAT_QTY_CRYPTED_CRC = 12,
    ENC_CUR_MAT_QTY_CRC = 13,
    ENC_CONTENT = 14,
};
uint16_t encryption_crc[] = {0x0,0x0C0C1,0x0C181,0x140,0x0C301,0x3C0,0x280,0x0C241,0x0C601,
    0x06C0,0x780,0x0C741,0x500,0x0C5C1,0x0C481,0x440,0x0CC01,0x0CC0,
    0x0D80,0x0CD41,0x0F00,0x0CFC1,0x0CE81,0x0E40,0x0A00,0x0CAC1,
    0x0CB81,0x0B40,0x0C901,0x9C0,0x880,0x0C841,0x0D801,0x18C0,0x1980,
    0x0D941,0x1B00,0x0DBC1,0x0DA81,0x1A40,0x1E00,0x0DEC1,0x0DF81,
    0x1F40,0x0DD01,0x1DC0,0x1C80,0x0DC41,0x1400,0x0D4C1,0x0D581,
    0x1540,0x0D701,0x17C0,0x1680,0x0D641,0x0D201,0x12C0,0x1380,
    0x0D341,0x1100,0x0D1C1,0x0D081,0x1040,0x0F001,0x30C0,0x3180,
    0x0F141,0x3300,0x0F3C1,0x0F281,0x3240,0x3600,0x0F6C1,0x0F781,
    0x3740,0x0F501,0x35C0,0x3480,0x0F441,0x3C00,0x0FCC1,0x0FD81,
    0x3D40,0x0FF01,0x3FC0,0x3E80,0x0FE41,0x0FA01,0x3AC0,0x3B80,
    0x0FB41,0x3900,0x0F9C1,0x0F881,0x3840,0x2800,0x0E8C1,0x0E981,
    0x2940,0x0EB01,0x2BC0,0x2A80,0x0EA41,0x0EE01,0x2EC0,0x2F80,
    0x0EF41,0x2D00,0x0EDC1,0x0EC81,0x2C40,0x0E401,0x24C0,0x2580,
    0x0E541,0x2700,0x0E7C1,0x0E681,0x2640,0x2200,0x0E2C1,0x0E381,
    0x2340,0x0E101,0x21C0,0x2080,0x0E041,0x0A001,0x60C0,0x6180,
    0x0A141,0x6300,0x0A3C1,0x0A281,0x6240,0x6600,0x0A6C1,0x0A781,
    0x6740,0x0A501,0x65C0,0x6480,0x0A441,0x6C00,0x0ACC1,0x0AD81,
    0x6D40,0x0AF01,0x6FC0,0x6E80,0x0AE41,0x0AA01,0x6AC0,0x6B80,
    0x0AB41,0x6900,0x0A9C1,0x0A881,0x6840,0x7800,0x0B8C1,0x0B981,
    0x7940,0x0BB01,0x7BC0,0x7A80,0x0BA41,0x0BE01,0x7EC0,0x7F80,
    0x0BF41,0x7D00,0x0BDC1,0x0BC81,0x7C40,0x0B401,0x74C0,0x7580,
    0x0B541,0x7700,0x0B7C1,0x0B681,0x7640,0x7200,0x0B2C1,0x0B381,
    0x7340,0x0B101,0x71C0,0x7080,0x0B041,0x5000,0x90C1,0x9181,0x5140,
    0x9301,0x53C0,0x5280,0x9241,0x9601,0x56C0,0x5780,0x9741,0x5500,
    0x95C1,0x9481,0x5440,0x9C01,0x5CC0,0x5D80,0x9D41,0x5F00,0x9FC1,
    0x9E81,0x5E40,0x5A00,0x9AC1,0x9B81,0x5B40,0x9901,0x59C0,0x5880,
    0x9841,0x8801,0x48C0,0x4980,0x8941,0x4B00,0x8BC1,0x8A81,0x4A40,
    0x4E00,0x8EC1,0x8F81,0x4F40,0x8D01,0x4DC0,0x4C80,0x8C41,0x4400,
    0x84C1,0x8581,0x4540,0x8701,0x47C0,0x4680,0x8641,0x8201,0x42C0,
    0x4380,0x8341,0x4100,0x81C1,0x8081,0x4040};

crypto_t *crypto_new() {
	return (crypto_t *)malloc(sizeof(crypto_t));
}

void crypto_free(crypto_t *crypto) {
	if (crypto) {
		free(crypto);
	}
}

uint8_t crypto_encrypt_canister(crypto_t *crypto, uint8_t *machine_number, uint8_t *uid, uint8_t *in_buf, uint8_t *out_buf, size_t buflen) {
    uint16_t crc;
    uint32_t i;

    memcpy((void *)&out_buf[encryption_map[8]], (void *)&in_buf[encryption_map[8]], encryption_len[8]);
    memcpy((void *)&out_buf[encryption_map[9]], (void *)&in_buf[encryption_map[9]], encryption_len[9]);

    // Create key CRC
    printf("[i] Computing key CRC ... ");
    crc = 0;
    for (i = encryption_map[8]; i < encryption_map[8] + encryption_len[8]; ++i) {
        crc = crypto_crc16(crypto, in_buf[i], crc);
    }
    *(uint16_t *)&out_buf[encryption_map[9]] = crc;
    printf("%4X\n", crc);

    // Create current manterial quantity CRC
    printf("[i] Computing current material quantity CRC ... ");
    crc = 0;
    for (i = encryption_map[11]; i < encryption_map[11] + encryption_len[11]; ++i) {
        crc = crypto_crc16(crypto, in_buf[i], crc);
    }
    *(uint16_t *)&out_buf[encryption_map[13]] = crc;
    printf("%4X\n", crc);

    // Create plain text CRC
    printf("[i] Computing plain text CRC ... ");
    crc = 0;
    for (i = encryption_map[14]; i < encryption_map[14] + encryption_len[14] - 8; ++i) {
        crc = crypto_crc16(crypto, in_buf[i], crc);
    }
    *(uint16_t *)&out_buf[encryption_map[6]] = crc;
    printf("%4X\n", crc);

    // Building key
    printf("[i] Building key ... ");
    crypto_init_key(crypto, machine_number, uid, in_buf, 0x68);
    printf("done.\n");

    // Encrypt content
    printf("[i] Encrypting content ... ");
    for (i=0; i<encryption_len[14] - 8; i+=8) {
        crypto_encrypt(crypto, &in_buf[i], &out_buf[i], 8);
    }
    printf("done.\n");

    // Encrypt current material quantity
    printf("[i] Encrypting current material qty ... ");
    for (i=0; i<encryption_len[11]; i+=8) {
        crypto_encrypt(crypto, &in_buf[encryption_map[11] + i], &out_buf[encryption_map[11] + i], 8);
    }
    printf("done.\n");

    // Create plain text CRC
    printf("[i] Computing crypted text CRC ... ");
    crc = 0;
    for (i = encryption_map[14]; i < encryption_map[14] + encryption_len[14] - 8; ++i) {
        crc = crypto_crc16(crypto, out_buf[i], crc);
    }
    *(uint16_t *)&out_buf[encryption_map[7]] = crc;
    printf("%4X\n", crc);

    // Compute current material quantity crypted CRC
    printf("[i] Computing current material quantity crypted CRC ... ");
    crc = 0;
    for (i = encryption_map[11]; i < encryption_map[11] + encryption_len[11]; ++i) {
        crc = crypto_crc16(crypto, out_buf[i], crc);
    }
    *(uint16_t *)&out_buf[encryption_map[12]] = crc;
    printf("%4X\n", crc);

    return 0;
}

uint8_t crypto_decrypt_canister(crypto_t *crypto, uint8_t *machine_number, uint8_t *uid, uint8_t *in_buf, uint8_t *out_buf, size_t buflen) {
    uint16_t crc;
    uint32_t i;

    memcpy((void *)&out_buf[encryption_map[8]], (void *)&in_buf[encryption_map[8]], encryption_len[8]);
    memcpy((void *)&out_buf[encryption_map[9]], (void *)&in_buf[encryption_map[9]], encryption_len[9]);

    // Validate key CRC
    printf("[i] Validating key CRC ... ");
    crc = 0;
    for (i = encryption_map[8]; i < encryption_map[8] + encryption_len[8]; ++i) {
        crc = crypto_crc16(crypto, in_buf[i], crc);
    }

    if (crc != *(uint16_t *)&in_buf[encryption_map[9]]) {
        // Invalid key CRC
        printf("invalid.\n");
        printf("\t%4X != %4X\n", crc, *(uint16_t *)&in_buf[encryption_map[9]]);
        return 1;
    }
    printf("valid.\n");

    // Building key
    printf("[i] Building key ... ");
    crypto_init_key(crypto, machine_number, uid, in_buf, 0x68);
    printf("done.\n");

    // Decrypt content
    printf("[i] Decrypting content ... ");
    for (i=0; i<encryption_len[14] - 8; i+=8) {
        crypto_decrypt(crypto, &in_buf[i], &out_buf[i], 8);
    }
    printf("done.\n");

    // Decrypt current material quantity
    printf("[i] Decrypting current material qty ... ");
    for (i=0; i<encryption_len[11]; i+=8) {
        crypto_decrypt(crypto, &in_buf[encryption_map[11] + i], &out_buf[encryption_map[11] + i], 8);
    }
    printf("done.\n");

    // Validate current material quantity crypted CRC
    printf("[i] Validating current material qty crypted CRC ... ");
    crc = 0;
    for (i = encryption_map[11]; i < encryption_map[11] + encryption_len[11]; ++i) {
        crc = crypto_crc16(crypto, in_buf[i], crc);
    }
    if (crc != *(uint16_t *)&in_buf[encryption_map[12]]) {
        // Invalid CRC 2
        printf("invalid.\n");
        printf("\t%4X != %4X\n", crc, *(uint16_t *)&in_buf[encryption_map[12]]);
        //return 2;
    }
    printf("valid.\n");

    // Validate plain text CRC
    printf("[i] Validating plain text CRC ... ");
    crc = 0;
    for (i = encryption_map[14]; i < encryption_map[14] + encryption_len[14] - 8; ++i) {
        crc = crypto_crc16(crypto, out_buf[i], crc);
    }
    if (crc != *(uint16_t *)&in_buf[encryption_map[6]]) {
        printf("invalid.\n");
        printf("\t%4X != %4X\n", crc, *(uint16_t *)&in_buf[encryption_map[6]]);
        //return 3;
    }
    printf("valid.\n");

    memcpy((void *)&out_buf[encryption_map[6]], (void *)&in_buf[encryption_map[6]], encryption_len[6]);

    // validate current material quantity crc
    printf("[i] Validating current material quantity crc ... ");
    crc = 0;
    for (i = encryption_map[11]; i < encryption_map[11] + encryption_len[11]; ++i) {
        crc = crypto_crc16(crypto, out_buf[i], crc);
    }
    if (crc != *(uint16_t *)&in_buf[encryption_map[13]]) {
        printf("invalid.\n");
        printf("\t%4X != %4X\n", crc, *(uint16_t *)&in_buf[encryption_map[13]]);
        //return 4;
    }
    printf("valid.\n");

    return 0;
}

uint8_t crypto_init_key(crypto_t *crypto, uint8_t *machine_number, uint8_t *uid, uint8_t *crypted, size_t cryptedlen) {
    crypto->key[0] = ~crypted[encryption_map[8]];
    crypto->key[1] = ~crypted[encryption_map[8]+2];
    crypto->key[2] = ~uid[5];
    crypto->key[3] = ~crypted[encryption_map[8]+6];
    crypto->key[4] = ~machine_number[0];
    crypto->key[5] = ~machine_number[2];
    crypto->key[6] = ~uid[2];
    crypto->key[7] = ~machine_number[6];
    crypto->key[8] = ~machine_number[7];
    crypto->key[9] = ~uid[6];
    crypto->key[10] = ~machine_number[3];
    crypto->key[11] = ~machine_number[1];
    crypto->key[12] = ~crypted[encryption_map[8]+7];
    crypto->key[13] = ~uid[1];
    crypto->key[14] = ~crypted[encryption_map[8]+3];
    crypto->key[15] = ~crypted[encryption_map[8]+1];

    return 0;
}

uint8_t crypto_init_key2(crypto_t *crypto, uint8_t *machine_number, uint8_t *crypted, size_t cryptedlen) {
    crypto->key[0] = ~crypted[encryption_map[8]];
    crypto->key[1] = ~crypted[encryption_map[8]+2];
    crypto->key[2] = ~crypted[encryption_map[8]+4];
    crypto->key[3] = ~crypted[encryption_map[8]+6];
    crypto->key[4] = ~machine_number[0];
    crypto->key[5] = ~machine_number[2];
    crypto->key[6] = ~machine_number[4];
    crypto->key[7] = ~machine_number[6];
    crypto->key[8] = ~machine_number[7];
    crypto->key[9] = ~machine_number[5];
    crypto->key[10] = ~machine_number[3];
    crypto->key[11] = ~machine_number[1];
    crypto->key[12] = ~crypted[encryption_map[8]+7];
    crypto->key[13] = ~crypted[encryption_map[8]+5];
    crypto->key[14] = ~crypted[encryption_map[8]+3];
    crypto->key[15] = ~crypted[encryption_map[8]+1];

    return 0;
}

ssize_t crypto_encrypt(crypto_t *crypto, uint8_t *in_buf, uint8_t *out_buf, size_t buflen) {
    DESX_CBCInit(&crypto->context, crypto->key, crypto->iv, 1);
    DESX_CBCUpdate(&crypto->context, out_buf, in_buf, buflen);
    DESX_CBCRestart(&crypto->context);

	return buflen;
}

ssize_t crypto_decrypt(crypto_t *crypto, uint8_t *in_buf, uint8_t *out_buf, size_t buflen) {
    DESX_CBCInit(&crypto->context, crypto->key, crypto->iv, 0);
    DESX_CBCUpdate(&crypto->context, out_buf, in_buf, buflen);
    DESX_CBCRestart(&crypto->context);
	return buflen;
}

uint16_t crypto_crc16(crypto_t *crypto, uint8_t data, uint16_t crc) {
    return (uint16_t)encryption_crc[(uint8_t)(crc ^ data)] ^ (crc >> 8);
}
