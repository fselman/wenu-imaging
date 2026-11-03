#include "pixelmap_flags8.h"
#include <ctype.h>
#include <string.h>

static int shape(int x, int y) {
    return CHAR_BIT==8 && x>0 && y>0 && x<=MAX_COLUMN_NUMBER &&
        y<=MAX_LINE_NUMBER && x<=INT_MAX/y;
}
static int registry_valid(const char *r) {
    size_t i;
    if (!r || !*r || strlen(r)>32) return 0;
    for (i=0;r[i];++i) if (!isalnum((unsigned char)r[i]) && r[i]!='_' && r[i]!='-') return 0;
    return 1;
}
int pixelmap_flags8_selection_checked(const unsigned char *flags, int x, int y,
    unsigned int reject, pixelmap **out) {
    pixelmap *m;
    int i;
    if (!out || *out || !flags || !shape(x,y) || reject>255) return -1;
    m=pixelmap_new(x,y);
    if (!m) return -1;
    for (i=0;i<x*y;++i) m->data[i]=(binpix)((flags[i]&reject)==0);
    pixelmap_updatecount(m); *out=m; return 0;
}
int pixelmap_flags8_from_image_checked(const image_t *im, unsigned char **out) {
    unsigned char *flags;
    int i;
    if (!out || *out || !im || !im->data || !shape(im->lx,im->ly)) return -1;
    for (i=0;i<im->lx*im->ly;++i) {
        double v=im->data[i];
        if (!(v>=0 && v<=255) || floor(v)!=v) return -1;
    }
    flags=malloc((size_t)im->lx*(size_t)im->ly);
    if (!flags) return -1;
    for (i=0;i<im->lx*im->ly;++i) flags[i]=(unsigned char)im->data[i];
    *out=flags; return 0;
}
int pixelmap_flags8_write_checked(FILE *f, const unsigned char *flags,
    int x, int y, const char *registry) {
    qfits_header *h;
    char value[40];
    size_t n, padding;
    unsigned char zeros[2880];
    int status;
    if (!f || !flags || !shape(x,y) || !registry_valid(registry) || ftell(f)!=0) return -1;
    h=qfits_header_default();
    if (!h) return -1;
    qfits_header_add(h,"BITPIX","8","Unsigned 8-bit flags",NULL);
    qfits_header_add(h,"NAXIS","2",NULL,NULL);
    sprintf(value,"%d",x); qfits_header_add(h,"NAXIS1",value,NULL,NULL);
    sprintf(value,"%d",y); qfits_header_add(h,"NAXIS2",value,NULL,NULL);
    qfits_header_add(h,"MASKENC","REASON8","Zero means no detected reasons",NULL);
    strcpy(value,registry);
    qfits_header_add(h,"MASKREG",value,"Versioned bit-definition registry",NULL);
    status=qfits_header_dump(h,f); qfits_header_destroy(h);
    if (status!=0) return -1;
    n=(size_t)x*(size_t)y; padding=(2880-n%2880)%2880;
    memset(zeros,0,sizeof(zeros));
    if (fwrite(flags,1,n,f)!=n || (padding && fwrite(zeros,1,padding,f)!=padding) ||
        fflush(f)!=0 || ferror(f)) return -1;
    return 0;
}
int pixelmap_flags8_load_checked(const char *path, int hdu, const char *registry,
    unsigned char **out, int *width, int *height) {
    qfits_header *h;
    image_t *im;
    char *value;
    unsigned char *flags=NULL;
    int status;
    if (!path || hdu<0 || !registry_valid(registry) || !out || *out || !width || !height || width==height)
        return -1;
    h=qfits_header_readext((char *)path,hdu);
    if (!h) return -1;
    status=-1;
    if (qfits_header_getint(h,"BITPIX",0)!=8 || qfits_header_getint(h,"NAXIS",0)!=2 ||
        !shape(qfits_header_getint(h,"NAXIS1",0),qfits_header_getint(h,"NAXIS2",0)) ||
        qfits_header_getdouble(h,"BSCALE",1)!=1 || qfits_header_getdouble(h,"BZERO",0)!=0)
        goto done;
    value=qfits_header_getstr(h,"MASKENC");
    if (!value || strcmp(qfits_pretty_string(value),"REASON8")) goto done;
    value=qfits_header_getstr(h,"MASKREG");
    if (!value || strcmp(qfits_pretty_string(value),registry)) goto done;
    im=image_loadext((char *)path,hdu,0,1);
    if (!im) goto done;
    if (pixelmap_flags8_from_image_checked(im,&flags)==0) {
        *out=flags; *width=im->lx; *height=im->ly; status=0;
    }
    image_del(im);
done:
    qfits_header_destroy(h); return status;
}
