
default:	pkg_pfits pkg_mef

pkg_pfits:
	@(if test -d ./pfits ; then\
	(cd pfits ; $(MAKE)); \
	else (true) fi)

pkg_mef:
	@(if test -d ./mef ; then\
	(cd mef ; $(MAKE)); \
	else (true) fi)

clean veryclean:
	@(if test -d ./pfits ; then\
	(cd pfits ; $(MAKE) $@); \
	else (true) fi)
	@(if test -d ./mef ; then\
	(cd mef ; $(MAKE) $@); \
	else (true) fi)
