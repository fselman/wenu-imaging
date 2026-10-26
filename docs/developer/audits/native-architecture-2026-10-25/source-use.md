# Native source-use inventory — 25 October 2026

Generated from the compiler-assisted audit; see the parent report for method and limits.

Direct = unresolved symbol demand from the two MEF translation units, including their non-reached functions.
Potential calls = static path from main through direct calls/function references.
Object closure = conservative transitive archive-object demand; no executable was linked.
Not selected does not mean safe to delete; other programs/configurations are outside this root.

| Source | Direct demand | Potential-call functions | Object closure |
|---|---|---:|---|
| mefpp2/ins/mef/recipes/mefpp.c | — | 4 | yes |
| mefpp2/ins/mef/common/mefp_lib.c | yes | 28 | yes |
| mefpp2/src/iproc/corner.c | — | 0 | no |
| mefpp2/src/iproc/cube2image.c | yes | 1 | yes |
| mefpp2/src/iproc/cube_arith.c | yes | 2 | yes |
| mefpp2/src/iproc/cube_filters.c | — | 0 | no |
| mefpp2/src/iproc/cube_handling.c | yes | 5 | yes |
| mefpp2/src/iproc/cube_load.c | yes | 1 | yes |
| mefpp2/src/iproc/cube_save.c | — | 0 | yes |
| mefpp2/src/iproc/dead_pixels.c | — | 0 | yes |
| mefpp2/src/iproc/detect.c | — | 0 | yes |
| mefpp2/src/iproc/detect_ks.c | — | 0 | yes |
| mefpp2/src/iproc/detect_sq.c | — | 0 | yes |
| mefpp2/src/iproc/detector.c | yes | 2 | yes |
| mefpp2/src/iproc/extraction.c | yes | 1 | yes |
| mefpp2/src/iproc/fourier.c | — | 0 | yes |
| mefpp2/src/iproc/framelist.c | yes | 5 | yes |
| mefpp2/src/iproc/generate.c | — | 0 | yes |
| mefpp2/src/iproc/histogram.c | — | 0 | yes |
| mefpp2/src/iproc/history.c | — | 0 | yes |
| mefpp2/src/iproc/image_arith.c | yes | 6 | yes |
| mefpp2/src/iproc/image_filters.c | yes | 1 | yes |
| mefpp2/src/iproc/image_handling.c | yes | 3 | yes |
| mefpp2/src/iproc/image_intops.c | — | 0 | yes |
| mefpp2/src/iproc/image_io.c | — | 1 | yes |
| mefpp2/src/iproc/image_rtd.c | — | 1 | yes |
| mefpp2/src/iproc/image_stats.c | yes | 4 | yes |
| mefpp2/src/iproc/intimage.c | — | 0 | yes |
| mefpp2/src/iproc/irstd.c | — | 0 | no |
| mefpp2/src/iproc/matchpoint.c | — | 0 | no |
| mefpp2/src/iproc/photometry.c | — | 0 | yes |
| mefpp2/src/iproc/pixel_handling.c | yes | 2 | yes |
| mefpp2/src/iproc/pixelmaps.c | yes | 5 | yes |
| mefpp2/src/iproc/resampling.c | — | 0 | no |
| mefpp2/src/iproc/shift.c | — | 0 | no |
| mefpp2/src/iproc/slitposition.c | — | 0 | no |
| mefpp2/src/iproc/xcorrelation.c | — | 0 | no |
| mefpp2/src/math/chebyshev.c | — | 0 | no |
| mefpp2/src/math/doubles.c | — | 2 | yes |
| mefpp2/src/math/dstats.c | yes | 3 | yes |
| mefpp2/src/math/fft_base.c | — | 0 | yes |
| mefpp2/src/math/fit_curve.c | — | 3 | yes |
| mefpp2/src/math/function_1d.c | yes | 1 | yes |
| mefpp2/src/math/ipow.c | — | 0 | yes |
| mefpp2/src/math/legendre.c | — | 0 | yes |
| mefpp2/src/math/matrix.c | — | 0 | yes |
| mefpp2/src/math/median.c | yes | 7 | yes |
| mefpp2/src/math/optimization.c | — | 0 | yes |
| mefpp2/src/math/poly2d.c | — | 0 | no |
| mefpp2/src/math/polygon.c | — | 0 | yes |
| mefpp2/src/math/random.c | — | 0 | yes |
| mefpp2/src/spectro/spectral_lines.c | — | 0 | no |
| mefpp2/src/spectro/spectro_arcs.c | — | 0 | no |
| mefpp2/src/spectro/spectro_detect.c | — | 0 | no |
| mefpp2/src/spectro/spectro_wave.c | — | 0 | no |
| mefpp2/src/unix/calendar.c | — | 0 | no |
| mefpp2/src/unix/charmatrix.c | — | 3 | yes |
| mefpp2/src/unix/chronos.c | — | 0 | no |
| mefpp2/src/unix/cmdline.c | — | 0 | no |
| mefpp2/src/unix/comm.c | yes | 18 | yes |
| mefpp2/src/unix/dictionary.c | — | 0 | no |
| mefpp2/src/unix/e_config.c | yes | 1 | yes |
| mefpp2/src/unix/e_version.c | yes | 3 | yes |
| mefpp2/src/unix/file_handling.c | — | 1 | yes |
| mefpp2/src/unix/filelock.c | — | 0 | no |
| mefpp2/src/unix/filename.c | yes | 2 | yes |
| mefpp2/src/unix/filesys.c | — | 0 | no |
| mefpp2/src/unix/getopt.c | yes | 5 | yes |
| mefpp2/src/unix/gnuplot_i.c | — | 0 | yes |
| mefpp2/src/unix/iniparser.c | — | 0 | no |
| mefpp2/src/unix/manpage.c | — | 0 | no |
| mefpp2/src/unix/memstr.c | — | 0 | no |
| mefpp2/src/unix/parse_tok.c | — | 2 | yes |
| mefpp2/src/unix/pid_i.c | — | 0 | no |
| mefpp2/src/unix/ptrace.c | — | 0 | no |
| mefpp2/src/unix/rtd_i.c | — | 10 | yes |
| mefpp2/src/unix/show.c | — | 0 | no |
| mefpp2/src/unix/strlib.c | — | 2 | yes |
| mefpp2/src/unix/t_iso8601.c | yes | 6 | yes |
| mefpp2/src/unix/t_stamp.c | — | 1 | yes |
| mefpp2/src/unix/userid.c | — | 1 | yes |
| qfits52/src/byteswap.c | — | 3 | yes |
| qfits52/src/cache.c | — | 5 | yes |
| qfits52/src/expkey.c | — | 2 | yes |
| qfits52/src/fits_h.c | yes | 20 | yes |
| qfits52/src/fits_md5.c | — | 0 | yes |
| qfits52/src/fits_p.c | — | 3 | yes |
| qfits52/src/fits_rw.c | yes | 5 | yes |
| qfits52/src/get_name.c | — | 0 | no |
| qfits52/src/ieeefp-compat.c | — | 0 | no |
| qfits52/src/md5.c | — | 0 | yes |
| qfits52/src/pafs.c | yes | 3 | yes |
| qfits52/src/pixio.c | yes | 10 | yes |
| qfits52/src/qerror.c | — | 2 | yes |
| qfits52/src/simple.c | yes | 10 | yes |
| qfits52/src/t_iso8601.c | — | 0 | no |
| qfits52/src/tfits.c | — | 0 | no |
| qfits52/src/version.c | yes | 1 | yes |
| qfits52/src/xmemory.c | yes | 14 | yes |
