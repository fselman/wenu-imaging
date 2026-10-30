#include "original-xmemory.c"
int main(void) {
    FILE *stream;
    const char *name;
    xmemory_init(); xmemory_initialized = 1;
    xmemory_table.file_reg = 1;
    name = xmemory_tmpfilename(1);
    stream = fopen(name, "w"); if (!stream) return 2;
    fputs("unowned sentinel", stream); fclose(stream);
    xmemory_cleanup();
    if (access(name, F_OK) != 0) {
        puts("REPRODUCED: original cleanup deleted an unowned sentinel");
        return 1;
    }
    return 0;
}
