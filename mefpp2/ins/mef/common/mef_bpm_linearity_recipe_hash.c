/* SHA-256 file identity, FIPS 180-4 sections 4.1.2, 4.2.2 and 6.2.
 * macOS uses the system CommonCrypto implementation; other hosts retain the
 * portable construction below. Bounded streaming only; this code does not handle credentials or image math.
 */
#define _POSIX_C_SOURCE 200809L
#include "mef_bpm_linearity_recipe.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#ifdef __APPLE__
#include <CommonCrypto/CommonDigest.h>
#endif

#ifndef __APPLE__
static uint32_t rotate(uint32_t x, unsigned n)
{
    return (x >> n) | (x << (32 - n));
}

static void compress(uint32_t h[8], const unsigned char block[64])
{
    static const uint32_t k[64] = {
        0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
        0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
        0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
        0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
        0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
        0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
        0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
        0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
    };
    uint32_t w[64], a=h[0], b=h[1], c=h[2], d=h[3], e=h[4], f=h[5], g=h[6], z=h[7];
    size_t i;
    for (i=0; i<16; ++i) {
        const unsigned char *p=block+4*i;
        w[i]=((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];
    }
    for (; i<64; ++i) {
        uint32_t s0=rotate(w[i-15],7)^rotate(w[i-15],18)^(w[i-15]>>3);
        uint32_t s1=rotate(w[i-2],17)^rotate(w[i-2],19)^(w[i-2]>>10);
        w[i]=w[i-16]+s0+w[i-7]+s1;
    }
    for (i=0; i<64; ++i) {
        uint32_t t1=z+(rotate(e,6)^rotate(e,11)^rotate(e,25))+((e&f)^(~e&g))+k[i]+w[i];
        uint32_t t2=(rotate(a,2)^rotate(a,13)^rotate(a,22))+((a&b)^(a&c)^(b&c));
        z=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    h[0]+=a; h[1]+=b; h[2]+=c; h[3]+=d; h[4]+=e; h[5]+=f; h[6]+=g; h[7]+=z;
}

#endif

static int same_file(const struct stat *a, const struct stat *b)
{
#ifdef __APPLE__
    int time_equal=a->st_mtimespec.tv_sec==b->st_mtimespec.tv_sec &&
        a->st_mtimespec.tv_nsec==b->st_mtimespec.tv_nsec;
#else
    int time_equal=a->st_mtim.tv_sec==b->st_mtim.tv_sec && a->st_mtim.tv_nsec==b->st_mtim.tv_nsec;
#endif
    return time_equal && a->st_dev==b->st_dev && a->st_ino==b->st_ino &&
        a->st_size==b->st_size && a->st_mode==b->st_mode;
}

int mef_bpm_linearity_hash(const char *path, char hex[65])
{
#ifdef __APPLE__
    CC_SHA256_CTX state;
    unsigned char digest[CC_SHA256_DIGEST_LENGTH];
#else
    uint32_t h[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
    unsigned char tail[128]={0};
    uint64_t bits;
    size_t remainder=0;
#endif
    unsigned char buffer[65536];
    uint64_t bytes=0;
    size_t n, i;
    struct stat before, after;
    FILE *f=fopen(path,"rb");
    int okay=0;
    if (!f) return 0;
#ifdef __APPLE__
    if (CC_SHA256_Init(&state)!=1) goto done;
#endif
    if (fstat(fileno(f),&before) || !S_ISREG(before.st_mode)) goto done;
    while ((n=fread(buffer,1,sizeof(buffer),f))!=0) {
        if (bytes>UINT64_MAX/8-n) goto done;
        bytes+=n;
#ifdef __APPLE__
        if (CC_SHA256_Update(&state,buffer,(CC_LONG)n)!=1) goto done;
#else
        for (i=0; i+64<=n; i+=64) compress(h,buffer+i);
        remainder=n-i;
        if (remainder) {
            memcpy(tail,buffer+i,remainder);
            if (!feof(f)) goto done;
        }
#endif
    }
    if (ferror(f) || fstat(fileno(f),&after) || !same_file(&before,&after)) goto done;
#ifdef __APPLE__
    if (CC_SHA256_Final(digest,&state)!=1) goto done;
    for (i=0; i<sizeof(digest); ++i) snprintf(hex+2*i,3,"%02x",(unsigned)digest[i]);
#else
    tail[remainder]=0x80;
    bits=bytes*8;
    n=remainder<56?64:128;
    for (i=0; i<8; ++i) tail[n-1-i]=(unsigned char)(bits>>(8*i));
    compress(h,tail);
    if (n==128) compress(h,tail+64);
    for (i=0; i<8; ++i) snprintf(hex+8*i,9,"%08x",(unsigned)h[i]);
#endif
    okay=1;
done:
    if (fclose(f)) okay=0;
    return okay;
}

int mef_bpm_linearity_dependency_check(mef_bpm_linearity_dependency *dependency, int content)
{
    struct stat current, after;
    char digest[65];
    if (stat(dependency->path,&current) || !S_ISREG(current.st_mode)) return 0;
    if (!content) return same_file(&dependency->identity,&current);
    if ((dependency->identity.st_mode && !same_file(&dependency->identity,&current)) ||
        !mef_bpm_linearity_hash(dependency->path,digest) || strcmp(digest,dependency->sha256) ||
        stat(dependency->path,&after) || !same_file(&current,&after)) return 0;
    dependency->identity=after;
    return 1;
}

int mef_bpm_linearity_observe(mef_bpm_linearity_recipe *recipe)
{
    size_t i;
    for (i=0; i<recipe->dependency_count; ++i) {
        if (!mef_bpm_linearity_dependency_check(recipe->dependencies+i,0)) {
            recipe->diagnostic="A frozen input changed during processing";
            return 0;
        }
    }
    return 1;
}
