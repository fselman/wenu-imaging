/* Actual cube constructor plus exact MEF loader excerpt, with controlled services.
 * No recipe, real FITS I/O, qfits allocator or host-memory qualification is run. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void *raw_allocate(size_t size) { return malloc(size); }
static void raw_release(void *pointer) { free(pointer); }
#include "eclipse.h"
#include "mefp_lib.h"
#include "xmemory.h"

static int calls, fail_at, live, released_images;
static image_t input_image;
static pixelvalue input_pixels[4];
void *xmemory_malloc(size_t size, const char *file, int line)
{
    void *p;
    (void)file; (void)line;
    calls++;
    if (calls == fail_at) return NULL;
    p = raw_allocate(size);
    if (p == NULL) abort();
    live++;
    return p;
}
void xmemory_free(void *pointer, const char *file, int line)
{
    (void)file; (void)line;
    if (pointer != NULL) { live--; raw_release(pointer); }
    if (live < 0) abort();
}
void e_error(char *format, ...) { (void)format; }
void e_comment(int level, char *format, ...) { (void)level; (void)format; }
int debug_active(void) { return 0; }
int qfits_query_n_ext(char *name) { (void)name; return 2; }
image_t *mef_load_ext(char *name, int xt) { (void)name; (void)xt; return &input_image; }
void image_del(image_t *image)
{
    if (image == NULL) return; /* Production image_del accepts NULL. */
    if (image != &input_image || released_images != 0) abort();
    released_images++;
}
double image_getmean(image_t *image) { (void)image; return 0.0; }
cube_t *cube_load_strings(char **names, int n) { (void)names; (void)n; return NULL; }
#include "cube_loader_excerpt.inc"

int main(void)
{
    cube_t *cube;
    framelist list;
    char *name;
    int failure, i;
    input_image.lx = 2; input_image.ly = 2; input_image.data = input_pixels;
    for (i = 0; i < 4; i++) input_pixels[i] = (pixelvalue)i;
    /* Constructor structure/plane failure and success all leave balanced owners. */
    for (failure = 0; failure <= 2; failure++) {
        calls = live = released_images = 0; fail_at = failure;
        cube = cube_new(2, 2, 1);
        if (failure != 0) { if (cube != NULL || live != 0) return 1; }
        else {
            if (cube == NULL || cube->lx != 2 || cube->ly != 2 || cube->np != 1 || cube->plane[0] != NULL) return 2;
            cube_del(cube);
            if (live != 0) return 3;
        }
    }
    name = "controlled.fits"; list.n = 1; list.name = &name;
    /* The loader's extension array is allocation 1; cube structure/planes are 2/3. */
    for (failure = 0; failure <= 3; failure++) {
        if (failure == 1) continue; /* Outside the selected repair scope. */
        calls = live = released_images = 0; fail_at = failure;
        cube = mef_cube_framelist_load(&list, 1);
        if (failure != 0) {
            if (cube != NULL || live != 0 || released_images != 1) return 4;
        } else {
            if (cube == NULL || cube->plane[0] != &input_image || released_images != 0) return 5;
            cube_del(cube);
            if (live != 0 || released_images != 1) return 6;
        }
        for (i = 0; i < 4; i++) if (input_pixels[i] != (pixelvalue)i) return 7;
    }
    puts("Cube allocation/loaded-image owner controls passed; recipe launches: 0");
    return 0;
}
