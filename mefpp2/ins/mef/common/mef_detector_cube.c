#include "mef_detector_cube.h"
#include "mef_config_toml.h"
#include "mefp_lib.h"
#include "mef_measure_plan_internal.h"
#include "mef_linearity_command_internal.h"

const mef_detector_plane *mef_detector_cube_find(const mef_detector_cube *cube,const char *path,int hdu)
{
    if(!cube || !path) return NULL;
    for(size_t i=0;i<cube->count;++i)
        if(cube->planes[i].hdu==hdu && !strcmp(cube->planes[i].path,path)) return cube->planes+i;
    return NULL;
}

const mef_detector_plane *mef_detector_cube_bound(const mef_detector_cube *cube,
    const mef_layout_map *map,const char *detector)
{
    const mef_bound_detector *binding=mef_layout_find(map,detector);
    return binding?mef_detector_cube_find(cube,mef_layout_map_path(map),binding->image.hdu_index):NULL;
}

void mef_detector_cube_destroy(mef_detector_cube *cube)
{
    if(!cube) return;
    for(size_t i=0;i<cube->count;++i) {
        (free)(cube->planes[i].path);
        image_del(cube->planes[i].raw);
        image_del(cube->planes[i].active);
        (free)(cube->planes[i].trace);
    }
    image_del(cube->master);pixelmap_del(cube->binary);if(cube->flags)free(cube->flags);
    mef_config_destroy(cube->configuration);
    memset(cube,0,sizeof(*cube));
}

static int ingest_plane(mef_detector_cube *cube,source *input,const plan *p,
    size_t slot,int bx,int by,int rw,int rh,size_t budget,int is_flat)
{
    mef_linearity_prepare_frame_result *prepared=NULL;
    if(mef_detector_cube_find(cube,input->path,input->hdu)) return 1;
    if(cube->count==128 || !bind_source(input,p,&cube->settings,slot,bx,by,0,rw,rh)) return 0;
    mef_detector_plane *plane=cube->planes+cube->count++;
    plane->path=(strdup)(input->path);plane->hdu=input->hdu;plane->is_flat=is_flat;
    if(!plane->path || mef_layout_load(input->map,p->value[0],&plane->raw,NULL)!=MEF_OK) return 0;
    ++cube->image_loads;
    mef_linearity_prepare_frame_input request={plane->raw,is_flat?cube->master:NULL,
        cube->settings,is_flat && cube->master?MEF_PREPARE_FLAT:MEF_PREPARE_BIAS,budget};
    if(mef_linearity_prepare_frame(&request,NULL,&prepared)!=MEF_OK) return 0;
    ++cube->corrections;
    plane->active=prepared->active;prepared->active=NULL;
    plane->trace=prepared->row_correction;prepared->row_correction=NULL;
    plane->rows=prepared->rows;
    mef_linearity_prepare_frame_destroy(prepared);
    if(is_flat) ++cube->flat_count;
    else {
        image_del(plane->active);plane->active=NULL;
        int reference=0;
        for(int j=0;j<2;++j) if(input->hdu==p->bias[j].hdu && !strcmp(input->path,p->bias[j].path)) reference=1;
        if(!reference) {image_del(plane->raw);plane->raw=NULL;}
    }
    return 1;
}

int mef_detector_cube_ingest(mef_detector_cube *cube,int argc,char **argv,int qc)
{
    plan p;source master;char diagnostic[256];size_t slot,budget;
    int bx,by,rw,rh,good,okay=0;
    FILE *list=NULL;char *line=NULL;size_t capacity=0;
    memset(cube,0,sizeof(*cube));memset(&p,0,sizeof(p));memset(&master,0,sizeof(master));
    cube->qc=qc;
    if(argc!=16 || !read_plan(argv[4],&p) ||
       !unsigned_number(p.value[2],4095,&slot) || !unsigned_number(p.value[16],SIZE_MAX,&budget) ||
       !int_number(p.value[8],64,&bx) || !int_number(p.value[9],64,&by) ||
       !int_number(p.value[23],MAX_COLUMN_NUMBER,&rw) || !int_number(p.value[24],MAX_LINE_NUMBER,&rh) ||
       !int_number(p.value[11],1,&good)) goto done;
    mef_config_toml_initialize();
    if(mef_config_from_toml(argv[1],NULL,&cube->configuration,diagnostic,sizeof(diagnostic))!=MEF_OK ||
       mef_config_bias_settings(cube->configuration,slot,&cube->settings)!=MEF_OK) goto done;

    /* Calibrations are immutable inputs, never inferred or rebuilt here. */

    master.path=argv[5];master.asset=argv[7];
    if(strcmp(master.path,"-")) {
        if(!int_number(argv[6],4095,&master.hdu) || !bind_master(&master,&p,&cube->settings,slot,bx,by) ||
           mef_layout_load(master.map,p.value[0],&cube->master,NULL)!=MEF_OK) goto done;
        ++cube->image_loads;
    }
    if(p.has_bpm) {
        if(!bind_source(&p.bpm,&p,&cube->settings,slot,bx,by,1,rw,rh)) goto done;
        if(!strcmp(p.value[10],"binary")) {
            if(mef_layout_load_bpm(p.bpm.map,p.value[0],good,&cube->binary,NULL)!=MEF_OK) goto done;
        } else if(!strcmp(p.value[10],"reason8")) {
            if(pixelmap_flags8_load_checked(p.bpm.path,p.bpm.hdu,p.value[12],&cube->flags,
                &cube->mask_width,&cube->mask_height)) goto done;
        } else goto done;
        ++cube->image_loads;
    }
    for(int i=0;i<p.flats;++i)
        if(!ingest_plane(cube,p.flat+i,&p,slot,bx,by,rw,rh,budget,1)) goto done;

    /* Bias traces and raw pair evidence use these same loaded planes. */

    list=fopen(argv[8],"rb");
    if(!list || getline(&line,&capacity,list)<0 ||
       strcmp(line,"input_index\thdu\tasset\tpath\taccepted\n")) goto done;
    while(getline(&line,&capacity,list)>=0) {
        char *cells[5];source bias;memset(&bias,0,sizeof(bias));
        size_t n=strlen(line);if(!n || line[n-1]!='\n') goto done;line[n-1]=0;
        if(fields(line,cells,5)!=5 || !int_number(cells[1],4095,&bias.hdu)) goto done;
        bias.asset=cells[2];bias.path=cells[3];
        int accepted=ingest_plane(cube,&bias,&p,slot,bx,by,rw,rh,budget,0);
        mef_layout_map_destroy(bias.map);
        if(!accepted) goto done;
    }
    okay=!ferror(list);
done:
    if(list) fclose(list);
    (free)(line);
    for(int i=0;i<p.flats;++i) mef_layout_map_destroy(p.flat[i].map);
    mef_layout_map_destroy(master.map);mef_layout_map_destroy(p.bpm.map);(free)(p.text);
    if(!okay) mef_detector_cube_destroy(cube);
    return okay;
}
