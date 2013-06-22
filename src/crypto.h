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

#ifndef CRYPTO_H
#define CRYPTO_H

#include <stdint.h>

#include "des.h"

struct crypto {
    uint8_t key[0x10];
    uint8_t iv[0x100];
    DESX_CBC_CTX context;
};

typedef struct crypto crypto_t;

crypto_t *crypto_new();
void crypto_free(crypto_t *crypto);
uint8_t crypto_init_key(crypto_t *crypto, uint8_t *machine_number, uint8_t *uid, uint8_t *crypted, size_t cryptedlen);
uint8_t crypto_init_key2(crypto_t *crypto, uint8_t *machine_number, uint8_t *crypted, size_t cryptedlen);
ssize_t crypto_encrypt(crypto_t *crypto, uint8_t *in_buf, uint8_t *out_buf, size_t buflen);
ssize_t crypto_decrypt(crypto_t *crypto, uint8_t *in_buf, uint8_t *out_buf, size_t buflen);
uint16_t crypto_crc16(crypto_t *crypto, uint8_t data, uint16_t crc);

uint8_t crypto_decrypt_canister(crypto_t *crypto, uint8_t *machine_number, uint8_t *uid, uint8_t *in_buf, uint8_t *out_buf, size_t buflen);
uint8_t crypto_encrypt_canister(crypto_t *crypto, uint8_t *machine_number, uint8_t *uid, uint8_t *in_buf, uint8_t *outbuf, size_t buflen);

#endif
