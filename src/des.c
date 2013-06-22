/* blatantly stolen from somwhere on the internet... i don't remember where, from RSA i think.*/

#include <string.h>
#include <stdint.h>

#include "des.h"

static uint16_t bytebit[8] = {
    0200, 0100, 040, 020, 010, 04, 02, 01
};

static uint32_t bigbyte[24] = {
    0x800000L, 0x400000L, 0x200000L, 0x100000L,
    0x80000L,  0x40000L,  0x20000L,  0x10000L,
    0x8000L,   0x4000L,   0x2000L,   0x1000L,
    0x800L,    0x400L,    0x200L,    0x100L,
    0x80L,     0x40L,     0x20L,     0x10L,
    0x8L,      0x4L,      0x2L,      0x1L
};

static uint8_t totrot[16] = {
    1, 2, 4, 6, 8, 10, 12, 14, 15, 17, 19, 21, 23, 25, 27, 28
};

static uint8_t pc1[56] = {
    56, 48, 40, 32, 24, 16,  8,      0, 57, 49, 41, 33, 25, 17,
     9,  1, 58, 50, 42, 34, 26,     18, 10,  2, 59, 51, 43, 35,
    62, 54, 46, 38, 30, 22, 14,      6, 61, 53, 45, 37, 29, 21,
    13,  5, 60, 52, 44, 36, 28,     20, 12,  4, 27, 19, 11,  3
};

static uint8_t pc2[48] = {
    13, 16, 10, 23,  0,  4,  2, 27, 14,  5, 20,  9,
    22, 18, 11,  3, 25,  7, 15,  6, 26, 19, 12,  1,
    40, 51, 30, 36, 46, 54, 29, 39, 50, 44, 32, 47,
    43, 48, 38, 55, 33, 52, 45, 41, 49, 35, 28, 31
};

static uint8_t clorox[] = {
    0xBD,0x56,0xEA,0xF2,0xA2,0xF1,0xAC,0x2A,0xB0,0x93,0xD1,
    0x9C,0x1B,0x33,0xFD,0xD0,0x30,0x04,0xB6,0xDC,0x7D,0xDF,
    0x32,0x4B,0xF7,0xCB,0x45,0x9B,0x31,0xBB,0x21,0x5A,0x41,
    0x9F,0xE1,0xD9,0x4A,0x4D,0x9E,0xDA,0xA0,0x68,0x2C,0xC3,
    0x27,0x5F,0x80,0x36,0x3E,0xEE,0xFB,0x95,0x1A,0xFE,0xCE,
    0xA8,0x34,0xA9,0x13,0xF0,0xA6,0x3F,0xD8,0x0C,0x78,0x24,
    0xAF,0x23,0x52,0xC1,0x67,0x17,0xF5,0x66,0x90,0xE7,0xE8,
    0x07,0xB8,0x60,0x48,0xE6,0x1E,0x53,0xF3,0x92,0xA4,0x72,
    0x8C,0x08,0x15,0x6E,0x86,0x00,0x84,0xFA,0xF4,0x7F,0x8A,
    0x42,0x19,0xF6,0xDB,0xCD,0x14,0x8D,0x50,0x12,0xBA,0x3C,
    0x06,0x4E,0xEC,0xB3,0x35,0x11,0xA1,0x88,0x8E,0x2B,0x94,
    0x99,0xB7,0x71,0x74,0xD3,0xE4,0xBF,0x3A,0xDE,0x96,0x0E,
    0xBC,0x0A,0xED,0x77,0xFC,0x37,0x6B,0x03,0x79,0x89,0x62,
    0xC6,0xD7,0xC0,0xD2,0x7C,0x6A,0x8B,0x22,0xA3,0x5B,0x05,
    0x5D,0x02,0x75,0xD5,0x61,0xE3,0x18,0x8F,0x55,0x51,0xAD,
    0x1F,0x0B,0x5E,0x85,0xE5,0xC2,0x57,0x63,0xCA,0x3D,0x6C,
    0xB4,0xC5,0xCC,0x70,0xB2,0x91,0x59,0x0D,0x47,0x20,0xC8,
    0x4F,0x58,0xE0,0x01,0xE2,0x16,0x38,0xC4,0x6F,0x3B,0x0F,
    0x65,0x46,0xBE,0x7E,0x2D,0x7B,0x82,0xF9,0x40,0xB5,0x1D,
    0x73,0xF8,0xEB,0x26,0xC7,0x87,0x97,0x25,0x54,0xB1,0x28,
    0xAA,0x98,0x9D,0xA5,0x64,0x6D,0x7A,0xD4,0x10,0x81,0x44,
    0xEF,0x49,0xD6,0xAE,0x2E,0xDD,0x76,0x5C,0x2F,0xA7,0x1C,
    0xC9,0x09,0x69,0x9A,0x83,0xCF,0x29,0x39,0xB9,0xE9,0x4C,
    0xFF,0x43,0xAB
};

uint32_t Spbox[8][64] = {
    {0x01010400L, 0x00000000L, 0x00010000L, 0x01010404L,
    0x01010004L, 0x00010404L, 0x00000004L, 0x00010000L,
    0x00000400L, 0x01010400L, 0x01010404L, 0x00000400L,
    0x01000404L, 0x01010004L, 0x01000000L, 0x00000004L,
    0x00000404L, 0x01000400L, 0x01000400L, 0x00010400L,
    0x00010400L, 0x01010000L, 0x01010000L, 0x01000404L,
    0x00010004L, 0x01000004L, 0x01000004L, 0x00010004L,
    0x00000000L, 0x00000404L, 0x00010404L, 0x01000000L,
    0x00010000L, 0x01010404L, 0x00000004L, 0x01010000L,
    0x01010400L, 0x01000000L, 0x01000000L, 0x00000400L,
    0x01010004L, 0x00010000L, 0x00010400L, 0x01000004L,
    0x00000400L, 0x00000004L, 0x01000404L, 0x00010404L,
    0x01010404L, 0x00010004L, 0x01010000L, 0x01000404L,
    0x01000004L, 0x00000404L, 0x00010404L, 0x01010400L,
    0x00000404L, 0x01000400L, 0x01000400L, 0x00000000L,
    0x00010004L, 0x00010400L, 0x00000000L, 0x01010004L},
    {0x80108020L, 0x80008000L, 0x00008000L, 0x00108020L,
    0x00100000L, 0x00000020L, 0x80100020L, 0x80008020L,
    0x80000020L, 0x80108020L, 0x80108000L, 0x80000000L,
    0x80008000L, 0x00100000L, 0x00000020L, 0x80100020L,
    0x00108000L, 0x00100020L, 0x80008020L, 0x00000000L,
    0x80000000L, 0x00008000L, 0x00108020L, 0x80100000L,
    0x00100020L, 0x80000020L, 0x00000000L, 0x00108000L,
    0x00008020L, 0x80108000L, 0x80100000L, 0x00008020L,
    0x00000000L, 0x00108020L, 0x80100020L, 0x00100000L,
    0x80008020L, 0x80100000L, 0x80108000L, 0x00008000L,
    0x80100000L, 0x80008000L, 0x00000020L, 0x80108020L,
    0x00108020L, 0x00000020L, 0x00008000L, 0x80000000L,
    0x00008020L, 0x80108000L, 0x00100000L, 0x80000020L,
    0x00100020L, 0x80008020L, 0x80000020L, 0x00100020L,
    0x00108000L, 0x00000000L, 0x80008000L, 0x00008020L,
    0x80000000L, 0x80100020L, 0x80108020L, 0x00108000L},
    {0x00000208L, 0x08020200L, 0x00000000L, 0x08020008L,
    0x08000200L, 0x00000000L, 0x00020208L, 0x08000200L,
    0x00020008L, 0x08000008L, 0x08000008L, 0x00020000L,
    0x08020208L, 0x00020008L, 0x08020000L, 0x00000208L,
    0x08000000L, 0x00000008L, 0x08020200L, 0x00000200L,
    0x00020200L, 0x08020000L, 0x08020008L, 0x00020208L,
    0x08000208L, 0x00020200L, 0x00020000L, 0x08000208L,
    0x00000008L, 0x08020208L, 0x00000200L, 0x08000000L,
    0x08020200L, 0x08000000L, 0x00020008L, 0x00000208L,
    0x00020000L, 0x08020200L, 0x08000200L, 0x00000000L,
    0x00000200L, 0x00020008L, 0x08020208L, 0x08000200L,
    0x08000008L, 0x00000200L, 0x00000000L, 0x08020008L,
    0x08000208L, 0x00020000L, 0x08000000L, 0x08020208L,
    0x00000008L, 0x00020208L, 0x00020200L, 0x08000008L,
    0x08020000L, 0x08000208L, 0x00000208L, 0x08020000L,
    0x00020208L, 0x00000008L, 0x08020008L, 0x00020200L},
    {0x00802001L, 0x00002081L, 0x00002081L, 0x00000080L,
    0x00802080L, 0x00800081L, 0x00800001L, 0x00002001L,
    0x00000000L, 0x00802000L, 0x00802000L, 0x00802081L,
    0x00000081L, 0x00000000L, 0x00800080L, 0x00800001L,
    0x00000001L, 0x00002000L, 0x00800000L, 0x00802001L,
    0x00000080L, 0x00800000L, 0x00002001L, 0x00002080L,
    0x00800081L, 0x00000001L, 0x00002080L, 0x00800080L,
    0x00002000L, 0x00802080L, 0x00802081L, 0x00000081L,
    0x00800080L, 0x00800001L, 0x00802000L, 0x00802081L,
    0x00000081L, 0x00000000L, 0x00000000L, 0x00802000L,
    0x00002080L, 0x00800080L, 0x00800081L, 0x00000001L,
    0x00802001L, 0x00002081L, 0x00002081L, 0x00000080L,
    0x00802081L, 0x00000081L, 0x00000001L, 0x00002000L,
    0x00800001L, 0x00002001L, 0x00802080L, 0x00800081L,
    0x00002001L, 0x00002080L, 0x00800000L, 0x00802001L,
    0x00000080L, 0x00800000L, 0x00002000L, 0x00802080L},
    {0x00000100L, 0x02080100L, 0x02080000L, 0x42000100L,
    0x00080000L, 0x00000100L, 0x40000000L, 0x02080000L,
    0x40080100L, 0x00080000L, 0x02000100L, 0x40080100L,
    0x42000100L, 0x42080000L, 0x00080100L, 0x40000000L,
    0x02000000L, 0x40080000L, 0x40080000L, 0x00000000L,
    0x40000100L, 0x42080100L, 0x42080100L, 0x02000100L,
    0x42080000L, 0x40000100L, 0x00000000L, 0x42000000L,
    0x02080100L, 0x02000000L, 0x42000000L, 0x00080100L,
    0x00080000L, 0x42000100L, 0x00000100L, 0x02000000L,
    0x40000000L, 0x02080000L, 0x42000100L, 0x40080100L,
    0x02000100L, 0x40000000L, 0x42080000L, 0x02080100L,
    0x40080100L, 0x00000100L, 0x02000000L, 0x42080000L,
    0x42080100L, 0x00080100L, 0x42000000L, 0x42080100L,
    0x02080000L, 0x00000000L, 0x40080000L, 0x42000000L,
    0x00080100L, 0x02000100L, 0x40000100L, 0x00080000L,
    0x00000000L, 0x40080000L, 0x02080100L, 0x40000100L},
    {0x20000010L, 0x20400000L, 0x00004000L, 0x20404010L,
    0x20400000L, 0x00000010L, 0x20404010L, 0x00400000L,
    0x20004000L, 0x00404010L, 0x00400000L, 0x20000010L,
    0x00400010L, 0x20004000L, 0x20000000L, 0x00004010L,
    0x00000000L, 0x00400010L, 0x20004010L, 0x00004000L,
    0x00404000L, 0x20004010L, 0x00000010L, 0x20400010L,
    0x20400010L, 0x00000000L, 0x00404010L, 0x20404000L,
    0x00004010L, 0x00404000L, 0x20404000L, 0x20000000L,
    0x20004000L, 0x00000010L, 0x20400010L, 0x00404000L,
    0x20404010L, 0x00400000L, 0x00004010L, 0x20000010L,
    0x00400000L, 0x20004000L, 0x20000000L, 0x00004010L,
    0x20000010L, 0x20404010L, 0x00404000L, 0x20400000L,
    0x00404010L, 0x20404000L, 0x00000000L, 0x20400010L,
    0x00000010L, 0x00004000L, 0x20400000L, 0x00404010L,
    0x00004000L, 0x00400010L, 0x20004010L, 0x00000000L,
    0x20404000L, 0x20000000L, 0x00400010L, 0x20004010L},
    {0x00200000L, 0x04200002L, 0x04000802L, 0x00000000L,
    0x00000800L, 0x04000802L, 0x00200802L, 0x04200800L,
    0x04200802L, 0x00200000L, 0x00000000L, 0x04000002L,
    0x00000002L, 0x04000000L, 0x04200002L, 0x00000802L,
    0x04000800L, 0x00200802L, 0x00200002L, 0x04000800L,
    0x04000002L, 0x04200000L, 0x04200800L, 0x00200002L,
    0x04200000L, 0x00000800L, 0x00000802L, 0x04200802L,
    0x00200800L, 0x00000002L, 0x04000000L, 0x00200800L,
    0x04000000L, 0x00200800L, 0x00200000L, 0x04000802L,
    0x04000802L, 0x04200002L, 0x04200002L, 0x00000002L,
    0x00200002L, 0x04000000L, 0x04000800L, 0x00200000L,
    0x04200800L, 0x00000802L, 0x00200802L, 0x04200800L,
    0x00000802L, 0x04000002L, 0x04200802L, 0x04200000L,
    0x00200800L, 0x00000000L, 0x00000002L, 0x04200802L,
    0x00000000L, 0x00200802L, 0x04200000L, 0x00000800L,
    0x04000002L, 0x04000800L, 0x00000800L, 0x00200002L},
    {0x10001040L, 0x00001000L, 0x00040000L, 0x10041040L,
    0x10000000L, 0x10001040L, 0x00000040L, 0x10000000L,
    0x00040040L, 0x10040000L, 0x10041040L, 0x00041000L,
    0x10041000L, 0x00041040L, 0x00001000L, 0x00000040L,
    0x10040000L, 0x10000040L, 0x10001000L, 0x00001040L,
    0x00041000L, 0x00040040L, 0x10040040L, 0x10041000L,
    0x00001040L, 0x00000000L, 0x00000000L, 0x10040040L,
    0x10000040L, 0x10001000L, 0x00041040L, 0x00040000L,
    0x00041040L, 0x00040000L, 0x10041000L, 0x00001000L,
    0x00000040L, 0x10040040L, 0x00001000L, 0x00041040L,
    0x10001000L, 0x00000040L, 0x10000040L, 0x10040000L,
    0x10040040L, 0x10000000L, 0x00040000L, 0x10001040L,
    0x00000000L, 0x10041040L, 0x00040040L, 0x10000040L,
    0x10040000L, 0x10001000L, 0x10001040L, 0x00000000L,
    0x10041040L, 0x00041000L, 0x00041000L, 0x00001040L,
    0x00001040L, 0x00040040L, 0x10000000L, 0x10041000L}
};

static void scrunch(uint32_t *into, uint8_t *outof){
    *into    = (*outof++ & 0xffL) << 24;
    *into   |= (*outof++ & 0xffL) << 16;
    *into   |= (*outof++ & 0xffL) << 8;
    *into++ |= (*outof++ & 0xffL);
    *into    = (*outof++ & 0xffL) << 24;
    *into   |= (*outof++ & 0xffL) << 16;
    *into   |= (*outof++ & 0xffL) << 8;
    *into   |= (*outof   & 0xffL);
}

static void unscrunch(uint8_t *into, uint32_t *outof){
    *into++ = (uint8_t)((*outof >> 24) & 0xffL);
    *into++ = (uint8_t)((*outof >> 16) & 0xffL);
    *into++ = (uint8_t)((*outof >>  8) & 0xffL);
    *into++ = (uint8_t)( *outof++      & 0xffL);
    *into++ = (uint8_t)((*outof >> 24) & 0xffL);
    *into++ = (uint8_t)((*outof >> 16) & 0xffL);
    *into++ = (uint8_t)((*outof >>  8) & 0xffL);
    *into   = (uint8_t)( *outof        & 0xffL);
}

static void cookey(uint32_t *subkeys, uint32_t *kn, int encrypt){
    uint32_t *cooked, *raw0, *raw1;
    int increment;
    unsigned int i;

    raw1 = kn;
    cooked = encrypt ? subkeys : &subkeys[30];
    increment = encrypt ? 1 : -3;

    for (i = 0; i < 16; i++, raw1++) {
        raw0 = raw1++;
        *cooked    = (*raw0 & 0x00fc0000L) << 6;
        *cooked   |= (*raw0 & 0x00000fc0L) << 10;
        *cooked   |= (*raw1 & 0x00fc0000L) >> 10;
        *cooked++ |= (*raw1 & 0x00000fc0L) >> 6;
        *cooked    = (*raw0 & 0x0003f000L) << 12;
        *cooked   |= (*raw0 & 0x0000003fL) << 16;
        *cooked   |= (*raw1 & 0x0003f000L) >> 4;
        *cooked   |= (*raw1 & 0x0000003fL);
        cooked += increment;
    }
}

static void deskey(uint32_t subkeys[32], uint8_t key[8], int encrypt){
    uint32_t kn[32];
    int i, j, l, m, n;
    uint8_t pc1m[56], pcr[56];

    for(j = 0; j < 56; j++) {
        l = pc1[j];
        m = l & 07;
        pc1m[j] = (uint8_t)((key[l >> 3] & bytebit[m]) ? 1 : 0);
    }
    for(i = 0; i < 16; i++) {
        m = i << 1;
        n = m + 1;
        kn[m] = kn[n] = 0L;
        for(j = 0; j < 28; j++) {
            l = j + totrot[i];
            if (l < 28)
                pcr[j] = pc1m[l];
            else
                pcr[j] = pc1m[l - 28];
        }
        for(j = 28; j < 56; j++) {
            l = j + totrot[i];
            if (l < 56)
                pcr[j] = pc1m[l];
            else
                pcr[j] = pc1m[l - 28];
        }
        for(j = 0; j < 24; j++) {
            if(pcr[pc2[j]])
                kn[m] |= bigbyte[j];
            if(pcr[pc2[j+24]])
                kn[n] |= bigbyte[j];
        }
    }
    cookey(subkeys, kn, encrypt);

    memset(pc1m, 0, sizeof(pc1m));
    memset(pcr, 0, sizeof(pcr));
    memset(kn, 0, sizeof(kn));
}


#define F(l,r,key){\
    work = ((r >> 4) | (r << 28)) ^ *key;\
    l ^= Spbox[6][work & 0x3f];\
    l ^= Spbox[4][(work >> 8) & 0x3f];\
    l ^= Spbox[2][(work >> 16) & 0x3f];\
    l ^= Spbox[0][(work >> 24) & 0x3f];\
    work = r ^ *(key+1);\
    l ^= Spbox[7][work & 0x3f];\
    l ^= Spbox[5][(work >> 8) & 0x3f];\
    l ^= Spbox[3][(work >> 16) & 0x3f];\
    l ^= Spbox[1][(work >> 24) & 0x3f];\
}

static void desfunc(uint32_t *block, uint32_t *ks){
    unsigned long left,right,work;

    left = block[0];
    right = block[1];

    work = ((left >> 4) ^ right) & 0x0f0f0f0f;
    right ^= work;
    left ^= work << 4;
    work = ((left >> 16) ^ right) & 0xffff;
    right ^= work;
    left ^= work << 16;
    work = ((right >> 2) ^ left) & 0x33333333;
    left ^= work;
    right ^= (work << 2);
    work = ((right >> 8) ^ left) & 0xff00ff;
    left ^= work;
    right ^= (work << 8);
    right = (right << 1) | (right >> 31);
    work = (left ^ right) & 0xaaaaaaaa;
    left ^= work;
    right ^= work;
    left = (left << 1) | (left >> 31);

    /* Now do the 16 rounds */
    F(left,right,&ks[0]);
    F(right,left,&ks[2]);
    F(left,right,&ks[4]);
    F(right,left,&ks[6]);
    F(left,right,&ks[8]);
    F(right,left,&ks[10]);
    F(left,right,&ks[12]);
    F(right,left,&ks[14]);
    F(left,right,&ks[16]);
    F(right,left,&ks[18]);
    F(left,right,&ks[20]);
    F(right,left,&ks[22]);
    F(left,right,&ks[24]);
    F(right,left,&ks[26]);
    F(left,right,&ks[28]);
    F(right,left,&ks[30]);

    right = (right << 31) | (right >> 1);
    work = (left ^ right) & 0xaaaaaaaa;
    left ^= work;
    right ^= work;
    left = (left >> 1) | (left  << 31);
    work = ((left >> 8) ^ right) & 0xff00ff;
    right ^= work;
    left ^= work << 8;
    work = ((left >> 2) ^ right) & 0x33333333;
    right ^= work;
    left ^= work << 2;
    work = ((right >> 16) ^ left) & 0xffff;
    left ^= work;
    right ^= work << 16;
    work = ((right >> 4) ^ left) & 0x0f0f0f0f;
    left ^= work;
    right ^= work << 4;

    *block++ = right;
    *block = left;
}

// Initialize context.  Caller should clear the context when finished.
//   The key has the DES key, input whitener and output whitener concatenated.
//   This is the RSADSI special DES implementation.
void DESX_CBCInit(DESX_CBC_CTX *context, uint8_t *key, uint8_t *iv, int encrypt){
    uint8_t inw[8] = {0};
    uint8_t i=0,j=0;
    uint8_t clorox_i;
    uint8_t *v11, *v12;

    /* Save encrypt flag to context. */
    context->encrypt = encrypt;

    /* Pack initializing vector and whiteners into context. */
    scrunch(context->iv, iv);
    scrunch(context->inputWhitener, key + 8);

    /* special for output whitening */
    for (i=0; i<8; i++) {
        clorox_i = inw[0] ^ inw[1];
        v11 = &inw[0];
        v12 = &inw[1];
        for (j=0; j<7; j++) {
            *v11++ = *v12++;
        }
        *v11 = clorox[clorox_i] ^ key[i];
    }
    for (i=0; i<8; i++) {
        clorox_i = inw[0] ^ inw[1];
        v11 = &inw[0];
        v12 = &inw[1];
        for (j=0; j<7; j++) {
            *v11++ = *v12++;
        }
        *v11 = clorox[clorox_i] ^ key[i+8];
    }
    scrunch(context->outputWhitener, inw);

    /* Save the IV for use in Restart */
    scrunch(context->originalIV, iv);
    /* Precompute key schedule. */
    deskey (context->subkeys, key, encrypt);
}

// DESX-CBC block update operation. Continues a DESX-CBC encryption
//   operation, processing eight-byte message blocks, and updating
//   the context.  This is the RSADSI special DES implementation.
//   Requires len to a multiple of 8.
int DESX_CBCUpdate (DESX_CBC_CTX *context, uint8_t *output, uint8_t *input, size_t len){
    uint32_t inputBlock[2], work[2];
    unsigned int i;

    if(len % 8)
        return(RE_LEN);

    for(i = 0; i < len/8; i++)  {
        scrunch(inputBlock, &input[8*i]);

        /* Chain if encrypting, and xor with whitener. */
        if(context->encrypt == 0) {
            *work = *inputBlock ^ *context->outputWhitener;
            *(work+1) = *(inputBlock+1) ^ *(context->outputWhitener+1);
        }else{
            *work = *inputBlock ^ *context->iv ^ *context->inputWhitener;
            *(work+1) = *(inputBlock+1) ^ *(context->iv+1) ^ *(context->inputWhitener+1);
        }

        desfunc(work, context->subkeys);

        /* Xor with whitener, chain if decrypting, then update IV. */
        if(context->encrypt == 0) {
            *work ^= *context->iv ^ *context->inputWhitener;
            *(work+1) ^= *(context->iv+1) ^ *(context->inputWhitener+1);
            *(context->iv) = *inputBlock;
            *(context->iv+1) = *(inputBlock+1);
        }else{
            *work ^= *context->outputWhitener;
            *(work+1) ^= *(context->outputWhitener+1);
            *context->iv = *work;
            *(context->iv+1) = *(work+1);
        }
        unscrunch(&output[8*i], work);
    }
    memset(inputBlock, 0, sizeof(inputBlock));
    memset(work, 0, sizeof(work));
    return(ID_OK);
}

void DESX_CBCRestart(DESX_CBC_CTX *context){
    // Restore the original IV
    *context->iv = *context->originalIV;
    *(context->iv+1) = *(context->originalIV+1);
}

