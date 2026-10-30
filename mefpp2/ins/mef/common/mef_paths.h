/* Explicit serial-engine I/O paths. Legacy callers pass NULL. Refs #159. */
#ifndef MEF_PATHS_H
#define MEF_PATHS_H
#include "eclipse.h"
typedef struct mef_paths mef_paths;
struct _mef_bb_;
mef_paths *mef_paths_new(const char *, const char *, const char *, const char *);
void mef_paths_del(mef_paths *);
int mef_paths_bind(struct _mef_bb_ *);
framelist *mef_paths_frames(const mef_paths *, char *);
char *mef_paths_first(const mef_paths *, char *);
char *mef_paths_output(const mef_paths *, const char *);
int mef_paths_preflight(struct _mef_bb_ *);
int mef_paths_split_preflight(struct _mef_bb_ *, framelist *);
const char *mef_paths_work(const mef_paths *);
int mef_paths_finish(const mef_paths *);
#endif
