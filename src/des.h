/* blatantly stolen from somwhere on the internet... i don't remember where, from RSA i think.*/

#ifndef DES_H
#define DES_H

#define ID_OK   0
#define RE_LEN  1

typedef struct {
  uint32_t subkeys[32];                                             /* subkeys */
  uint32_t iv[2];                                       /* initializing vector */
  uint32_t inputWhitener[2];                                 /* input whitener */
  uint32_t outputWhitener[2];                               /* output whitener */
  uint32_t originalIV[2];                        /* for restarting the context */
  int encrypt;                                              /* encrypt flag */
} DESX_CBC_CTX;

void DESX_CBCInit(DESX_CBC_CTX *, uint8_t *, uint8_t *, int);
int DESX_DecryptBlock(DESX_CBC_CTX *context, uint8_t *output, uint8_t *input);
int DESX_CBCUpdate(DESX_CBC_CTX *, uint8_t *, uint8_t *, size_t len);
void DESX_CBCRestart(DESX_CBC_CTX *);

#endif // DES_H
