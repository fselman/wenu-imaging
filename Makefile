
include ./config.make

BINDIR = ./src/bin

CP      = cp -r
RM = rm -rf

PROGS = $(BINDIR)/3color \
	$(BINDIR)/average \
	$(BINDIR)/catcube \
	$(BINDIR)/ccube \
	$(BINDIR)/collapse \
	$(BINDIR)/deadpix \
	$(BINDIR)/distortion \
	$(BINDIR)/dumppix \
	$(BINDIR)/encircl \
	$(BINDIR)/extract \
	$(BINDIR)/extract_spec \
	$(BINDIR)/fft \
	$(BINDIR)/filt \
	$(BINDIR)/fit \
	$(BINDIR)/fitsppm \
	$(BINDIR)/flat \
	$(BINDIR)/histog \
	$(BINDIR)/imgen \
	$(BINDIR)/ipaste \
	$(BINDIR)/norm \
	$(BINDIR)/oddeven \
	$(BINDIR)/peak \
	$(BINDIR)/poisson \
	$(BINDIR)/setpix \
	$(BINDIR)/speedtest \
	$(BINDIR)/stcube \
	$(BINDIR)/std \
	$(BINDIR)/strehl \
	$(BINDIR)/thresh \
	$(BINDIR)/warping \
	$(BINDIR)/xcorr1d \
	$(BINDIR)/xcorr2d

QFITSPROGS = $(BINDIR)/dfits \
	$(BINDIR)/dtfits \
	$(BINDIR)/fitsmd5 \
	$(BINDIR)/fitsort \
	$(BINDIR)/flipx \
	$(BINDIR)/frameq \
	$(BINDIR)/hierarch28 \
	$(BINDIR)/iofits \
	$(BINDIR)/replacekey \
	$(BINDIR)/qextract

default:	pkg_qfits5 pkg_pfits pkg_main pkg_ins pkg_lang pkg_dfs


pkg_qfits5:
	@(if test -d ./qfits5 ; then\
	(cd qfits5 ; ./configure ; $(MAKE)); \
	else (true) fi)

pkg_pfits:
	@(if test -d ./ins/pfits ; then\
	(cd ins/pfits ; $(MAKE)); \
	else (true) fi)

pkg_main:
	@(if test -d ./src ; then\
	(cd src ; $(MAKE)); \
	else (true) fi)

pkg_ins:
	@(if test -d ./ins ; then\
	(cd ins ; $(MAKE)); \
	else (true) fi)

pkg_mef:
	@(if test -d ./ins/mef ; then\
	(cd ins/mef ; $(MAKE)); \
	else (true) fi)

pkg_lang:
	@(if test -d ./lang ; then\
	(cd lang ; $(MAKE)); \
	else (true) fi)

pkg_dfs:
	@(if test -d ./dfs ; then\
	(cd dfs ; $(MAKE)); \
	else (true) fi)

clean veryclean:
	@(if test -d ./src ; then\
	(echo "cleaning library tree..." ; cd src ; $(MAKE) $@); \
	else (true) fi)
	@(if test -d ./ins ; then\
	(echo "cleaning instrument tree..." ; cd ins ; $(MAKE) $@); \
	else (true) fi)
	@(if test -d ./lang ; then\
	(echo "cleaning language tree..." ; cd lang ; $(MAKE) $@); \
	else (true) fi)
	@(if test -d ./dfs ; then\
	(echo "cleaning dfs tree..." ; cd dfs ; $(MAKE) $@); \
	else (true) fi)
	@(if test -d ./qfits5 ; then\
	(echo "cleaning qfits5 tree..." ; cd qfits5 ; $(MAKE) $@); \
	else (true) fi)

install:
	echo "Installing eclipse and mefpp in " $(prefix)
	mkdir -p $(prefix)
	mkdir -p $(prefix)/bin
	@(if test -f $(BINDIR)/3color ; then\
	($(CP) $(BINDIR)/* $(prefix)/bin/.); \
	else (true) fi)

	mkdir -p $(prefix)/include
	@(if test -f $(BINDIR)/../include/ansiterm.h ; then\
	($(CP) $(BINDIR)/../include/*.h $(prefix)/include/.); \
	else (true) fi)

	mkdir -p $(prefix)/lib
	@(if test -f $(BINDIR)/../lib/libeclipse.a ; then\
	($(CP) $(BINDIR)/../lib/libeclipse.a $(prefix)/lib/.); \
	else (true) fi)

	mkdir -p $(prefix)/config
	@(if test -f $(BINDIR)/../../ins/mef/config/omegacam.paf ; then\
	($(CP) $(BINDIR)/../../ins/mef/config/*.paf $(prefix)/config/.); \
	else (true) fi)

	mkdir -p $(prefix)/static_cal
	@(if test -f $(BINDIR)/../../ins/mef/static_cal/OCAM_BPM_1x1.fits.fz ; then\
	($(CP) -f $(BINDIR)/../../ins/mef/static_cal/*.fits* $(prefix)/static_cal/. ; \
	cd $(prefix)/static_cal ; funpack -v *.fits.fz); \
	else (true) fi)

	mkdir -p $(prefix)/man
	@(if test -f ./man/man1/poisson.1 ; then\
	($(CP) -r ./man/* $(prefix)/man/.); \
	else (true) fi)

	@(if test -f ./bin/e_setup; then\
	($(CP) ./bin/* $(prefix)/bin/.); \
	else (true) fi)

