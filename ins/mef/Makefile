#
# eclipse/mef Makefile
# F. Selman, mutatis mutandi 
# the wfi Makefile by N. Devillard
#

# Path to eclipse library
ELIB = ../../src

#
# General definitions are all here
#

SUFFIXES = .o .c .h
OUTPUT_OPTION= -o $@
IFLAGS  = -I$(ELIB)/include -I./common -I$(QFITSDIR)/include

LD      = ld
LDFLAGS = -L$(ELIB)/lib -L$(QFITSDIR)/lib $(LFLAGS)
LDLIBS  = -leclipse -lqfits -lm $(LDLIBSLOCAL)
RM      = rm -f
RRM     = rm -rf
CP      = cp
MV      = mv

#
# Redefinition of implicit rules
#

SUFFIXES = .o .c .h .a .so .sl

COMPILE.c=$(CC) $(CFLAGS) $(IFLAGS) -c
LINK.c=$(CC) $(CFLAGS) $(IFLAGS) $(LDFLAGS)

.c:
	@($(LINK.c) -o $@ $< $(LDLIBS))
.c.o:
	@(echo "compiling $< ...")
	@($(COMPILE.c) -o $@ $<)

COMPF  = $(CFLAGS) $(IFLAGS)
LINKF  = $(LDFLAGS) $(LDLIBS)



#
# Eclipse directories
#

BINDIR = ../../bin


# Load compilation options (valid for all compiled sources hereafter) 
include $(ELIB)/../config.make


default: all

all: 	mef-common mef

clean:
	@(echo "cleaning MEF object files...")
	@($(RM) common/*.o recipes/*.o)

veryclean:
	@(echo "cleaning MEF recipes and object files...")
	@($(RM) common/*.o recipes/*.o $(MEFBINS))


#
# ************* MEF general routines
#

mef-common:	common/mefp_lib.o

SRC_MEFCOM = common/mefp_lib.c
OBJ_MEFCOM = $(SRC_MEFCOM:.c=.o)

common/mefp_lib.o:	common/mefp_lib.c common/wfi.h
	@(echo "compiling $@ ...")
	($(CC) $(COMPF) -c -o common/mefp_lib.o common/mefp_lib.c)

#
# ************* MEF recipes
#

MEFBINS =		$(BINDIR)/mefpp

mef:	$(MEFBINS)


$(BINDIR)/mefpp:	recipes/mefpp.c common/mefp_lib.o
	@(echo "compiling $@ ...")
	@($(CC) $(COMPF) -o $(BINDIR)/mefpp recipes/mefpp.c \
	$(OBJ_MEFCOM) $(LINKF))

# end of file
