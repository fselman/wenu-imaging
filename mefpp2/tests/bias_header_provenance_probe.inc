/* Included by the existing actual-kernel probe: selected cards, no ASDF mock. */
static const char *metadata_directory;
static size_t profile_detector_count=2;
static void selected_header_contract(mef_bias_product_qc *archive,const mef_product_paths *paths)
{
    FILE *f; qfits_header *h;
    unsigned char padding[2880]={0};char message[512];
    const mef_product_qc *p=mef_bias_product_qc_view(archive);
    const char *primary[]={"MJD-OBS","BOOL","I64","QUOTE","MISSING","UNDEF","DEXP"};
    const char *detector[]={"EXTNAME","ESO DET CHIP ID","MISSING"};
    assert(access(paths->fits,F_OK)!=0);
    f=fopen(paths->fits,"wb");assert(f);
    h=qfits_header_default();
    qfits_header_add(h,"BITPIX","8",NULL,NULL);
    qfits_header_add(h,"NAXIS","0",NULL,NULL);
    qfits_header_add(h,"EXTEND","T",NULL,NULL);
    qfits_header_add(h,"MJD-OBS","57000.125","Observation epoch",NULL);
    qfits_header_add(h,"BOOL","F",NULL,NULL);
    qfits_header_add(h,"I64","9223372036854775807",NULL,NULL);
    qfits_header_add(h,"QUOTE","'O''Brien'",NULL,NULL);
    qfits_header_add(h,"UNDEF",NULL,NULL,NULL);
    qfits_header_add(h,"DEXP","1.25D+01",NULL,NULL);
    assert(qfits_header_dump(h,f)==0);qfits_header_destroy(h);
    for(size_t i=0;i<p->detector_count;++i) {
        char id[80];snprintf(id,sizeof(id),"'%s'",p->detectors[i].id);
        h=qfits_header_new();
        qfits_header_append(h,"XTENSION","'IMAGE'",NULL,NULL);
        qfits_header_append(h,"BITPIX","-32",NULL,NULL);
        qfits_header_append(h,"NAXIS","2",NULL,NULL);
        qfits_header_append(h,"NAXIS1","3",NULL,NULL);
        qfits_header_append(h,"NAXIS2","4",NULL,NULL);
        qfits_header_append(h,"PCOUNT","0",NULL,NULL);
        qfits_header_append(h,"GCOUNT","1",NULL,NULL);
        qfits_header_append(h,"EXTNAME",id,NULL,NULL);
        qfits_header_append(h,"HIERARCH ESO DET CHIP ID","'physical-chip'",NULL,NULL);
        qfits_header_append(h,"END",NULL,NULL,NULL);
        assert(qfits_header_dump(h,f)==0);qfits_header_destroy(h);
        assert(fwrite(padding,1,sizeof(padding),f)==sizeof(padding));
    }
    assert(fclose(f)==0);
    int result=mef_bias_product_qc_headers(archive,primary,7,detector,3,
        "/synthetic/processing.toml","bias_recipe_schema_version=1\n",message,sizeof(message));
    if(result)fprintf(stderr,"HEADER_CAPTURE: %s\n",message);
    assert(result==0);
    assert(mef_bias_product_qc_check(archive,message,sizeof(message))==0);
    p=mef_bias_product_qc_view(archive);
    assert(p->header_card_count==7+3*p->detector_count);
    assert(p->header_cards[0].real==57000.125&&!strcmp(p->header_cards[0].type,"real"));
    assert(!strcmp(p->header_cards[1].type,"boolean")&&!p->header_cards[1].boolean);
    assert(p->header_cards[2].integer==INT64_MAX);
    assert(!strcmp(p->header_cards[3].value,"O'Brien"));
    assert(!p->header_cards[4].present&&!strcmp(p->header_cards[4].type,"missing"));
    assert(p->header_cards[5].present&&!strcmp(p->header_cards[5].type,"undefined"));
    assert(p->header_cards[6].real==12.5);
    for(size_t i=0;i<p->detector_count;++i) {
        const mef_qc_fits_card *c=p->header_cards+7+3*i;
        assert(c->hdu==(int)i+1&&!strcmp(c->detector_id,p->detectors[i].id));
        assert(!strcmp(c->value,p->detectors[i].id)&&strlen(c->card)==80);
        assert(!strcmp(c[1].value,"physical-chip")&&!c[2].present);
        h=qfits_header_readext((char *)paths->fits,(int)i+1);assert(h);
        assert(!memcmp(c->card,qfits_header_getline(h,"EXTNAME"),80));
        qfits_header_destroy(h);
    }
    /* Duplicate/invalid metadata refuses serialization, not first-wins. */
    mef_product_qc changed=*p;mef_qc_fits_card *cards=malloc(p->header_card_count*sizeof(*cards));
    assert(cards);memcpy(cards,p->header_cards,p->header_card_count*sizeof(*cards));
    changed.header_cards=cards;cards[1]=cards[0];
    assert(mef_product_qc_validate(&changed,message,sizeof(message))!=0);
    cards[1]=p->header_cards[1];cards[0].real=NAN;
    assert(mef_product_qc_validate(&changed,message,sizeof(message))!=0);
    free(cards);
}
