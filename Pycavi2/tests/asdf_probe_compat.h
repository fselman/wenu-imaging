#ifndef WENU_ASDF_PROBE_COMPAT_H
#define WENU_ASDF_PROBE_COMPAT_H

/* Test consumer only (#221). libasdf's installed config describes the library
 * compiler, which can support _Float16 while the consumer's GCC 10 does not.
 * Load that config first; its include guard prevents a later redefinition.
 * The optional accessor/_Generic entry are unused by this float64 probe.
 * No public structure, installed header, library binary or numeric type changes.
 */
#include <asdf/config.h>
#ifdef WENU_ASDF_PROBE_OMIT_FLOAT16
#undef ASDF_HAVE_FLOAT16
#endif
#include <asdf.h>

#endif
