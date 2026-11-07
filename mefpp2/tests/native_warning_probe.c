/* Focused known-answer checks for warning fixes; no observations/ASDF. */
#include "mefp_lib.h"
#include "md5.h"
#include <assert.h>
image_t *mef_corner_warning_reference(image_t *);

static void paths(void)
{
    char limit[4098]; size_t i;
    char *(*dirname_functions[2])(char *)={qfits_get_dir_name,get_dirname};
    char *(*root_functions[2])(char *)={qfits_get_root_name,get_rootname};
    for(i=0;i<2;++i) {
        assert(!strcmp(dirname_functions[i]("/a/b/image.fits"),"/a/b"));
        assert(!strcmp(dirname_functions[i]("/a/b/"),"/a"));
        assert(!strcmp(dirname_functions[i]("a///b///"),"a"));
        assert(!strcmp(dirname_functions[i]("/"),"/"));
        assert(!strcmp(dirname_functions[i]("image.fits"),"."));
        memset(limit,'x',4096); limit[0]='/'; limit[4096]='\0';
        assert(!strcmp(dirname_functions[i](limit),"/"));
        limit[4096]='x';limit[4097]='\0';assert(dirname_functions[i](limit)==NULL);
        assert(!strcmp(dirname_functions[i]("a"),"."));
        assert(!strcmp(root_functions[i]("/a/long-file-name.fits"),"/a/long-file-name"));
        assert(!strcmp(root_functions[i]("x.fits"),"x"));
    }
}
static void digest(void)
{
    static const char *messages[]={"","abc"};
    static const char *expected[]={"d41d8cd98f00b204e9800998ecf8427e","900150983cd24fb0d6963f7d28e17f72"};
    size_t i,j; struct MD5Context context; unsigned char output[16]; char hex[33];
    for(i=0;i<2;++i) {
        MD5Init(&context); MD5Update(&context,(const unsigned char *)messages[i],(unsigned)strlen(messages[i]));
        MD5Final(output,&context);
        for(j=0;j<16;++j) sprintf(hex+2*j,"%02x",output[j]);
        assert(!strcmp(hex,expected[i]));
        for(j=0;j<sizeof(context);++j) assert(((unsigned char *)&context)[j]==0);
    }
}
static void images(void)
{
    image_t *input=image_new(1024,640),*reference,*actual; int i,x,y,pattern;
    assert(input!=NULL);
    /* Existing histogram contract requires >=10 pixels per fixed entropy bin. */
    for(i=0;i<1024*640;++i) input->data[i]=0;
    assert(image_compute_entropy(input)==0);
    for(i=1;i<1024*640;i+=2) input->data[i]=1;
    assert(fabs(image_compute_entropy(input)-1.0)<1e-12);
    image_del(input);
    for(pattern=0;pattern<2;++pattern) {
        input=image_new(20,20);assert(input!=NULL);
        for(y=0;y<20;++y) for(x=0;x<20;++x)
            input->data[y*20+x]=(pixelvalue)(pattern?100*((x/5+y/5)%2)+x+2*y:3*x+y);
        reference=mef_corner_warning_reference(input);actual=image_detect_corners(input);
        assert(reference!=NULL && actual!=NULL);
        assert(!memcmp(reference->data,actual->data,400*sizeof(pixelvalue)));
        image_del(reference);image_del(actual);image_del(input);
    }
}
static void temperature(void)
{
    char types[4][8]={"G1.5IV","G2.5IV","G3.5IV","G4.5IV"};
    int expected[4]={5662,5562,5457,5352},i;
    for(i=0;i<4;++i) assert(irstd_get_star_temperature(types[i])==expected[i]);
}
int main(int argc,char **argv)
{
    mef_bb *bb;
    if(argc!=2) return 2;
    eclipse_init();set_logfile(0);set_debug(0);set_verbose(0);
    paths();digest();images();temperature();
    bb=mef_bb_new_from_paf(argv[1]);assert(bb!=NULL);
    assert(mef_create_orig_filename(bb,"bias")==NULL);
    assert(bb->orig_bias!=NULL && !strncmp(bb->orig_bias,"CMDP.",5));
    assert(mef_create_orig_filename(NULL,"bias")==NULL);
    mef_bb_del(bb);
    puts("PASS: path boundaries, MD5/context reset, entropy, exact corner reference, legacy temperature values and name-helper return");
    return 0;
}
