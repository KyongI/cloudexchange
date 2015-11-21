##############################################################################
#
# Common Path Define
#
##############################################################################
APP_PATH			= .
APP_HOME			= .

#COMMON Path
PROJECTPATH 			= $(APP_PATH)
RELEASEPATH 			= $(APP_HOME)
INCPATH 			= $(PROJECTPATH)/COMMON/INCLUDE
SRCPATH 			= $(PROJECTPATH)/COMMON/SRC
BINPATH 			= $(RELEASEPATH)/BIN
UTILPATH 			= $(RELEASEPATH)/UTIL

##############################################################################
# library
##############################################################################
LLIBTHREAD  = -lpthread

XML2_LIB	= -lxml2
XSLT_LIB	= -lxslt

##############################################################################
# Compiler Define
##############################################################################
#VIEW=1
ifeq ("$(VIEW)", "1")
	CC		= g++
	ARC		= ar
	ARC2		= ranlib
	ARC_FLAG2	= 
	RANLIB		= ranlib
else
	CC		= @echo "		CC	  " $@; g++
	ARC		= @echo "		ARC	 " $@; ar
	ARC2		= @echo "		ARC2	" $@; ranlib
	AR		= @echo "		AR	  " $@; ar
	RANLIB		= @echo "		RANLIB  " $@; ranlib
endif

ARC_FLAG   		= -r
#ARCH64 		= +DD64
#ARCH32 		= +DD32

##############################################################################
# Local Define
##############################################################################
CP = /bin/cp
MV = /bin/mv

##############################################################################
# DBMS Library Link Property 
##############################################################################
# MYSQL Include (INC_MYSQL_PATH)
# #####################################################################
INC_MYSQL_PATH = /usr/include/mysql
LIB_MYSQL_PATH = -lmysqlclient_r
#LIB_MYSQL_PATH = -L/usr/lib/x86_64-linux-gnu -lmysqlclient_r
# #####################################################################

###############################################################################
# Compiler Flag 
# Compile option flags(=CFLAGS) 
# Link library flags  (=LFLAGS)
# Include Path Flage (=IFLAGS)
# System Define Flags(=DEFINES)
# Local Define Flags (=MFLAGS)
# Bit for compile (=ARCH_FLAG)
###############################################################################
MFLAGS		=
ARCH_FLAG	= 
DEFINES 	= -D__LINUX -D_LINUX_ -D_LITTLE_ENDIAN_ -D_MYSQL_

#TODO: _LINUX_ __LINUX define ?ʿ?

IFLAGS 		= -I../INCLUDE \
			-I../INC \
			-I. \
			-I$(INCPATH)  \
			-I$(INC_MYSQL_PATH)

LFLAGS 		= $(LLIBTHREAD) $(LIB_MYSQL_PATH)

CFLAGS 		= -Wall -g -fPIC $(MFLAGS) $(DEFINES) $(LOCAL_DEFINES) $(IFLAGS)

###############################################################################
# 
# Suffix rules(convert: .pc -> .cpp -> .o)
# 
###############################################################################

.SUFFIXES:.cpp .C .o 

.cpp.o:
	$(CC) -c -o $*.o $(CFLAGS) $(IFLAGS) $*.cpp 

.C.o:
	$(CC) -c -o $*.o $(CFLAGS) $(IFLAGS) $*.C 

.PHONY: all clean install netinstall initial tags cscope distclean

all clean install netinstall initial tags cscope distclean ::
	@set -e;                        \
	for i in $(SUBDIR);             \
	do (                            \
		if [ $$i"NULL" != "NULL" ]; \
			then                        \
			echo "    CD " $(CURDIR)/$$i;   \
			$(MAKE) -C $$i $@;      \
		fi                          \
	);                              \
	done; 
