#	Makefile.inc

ARCH 		:= $(shell uname -m | sed -e s/i.86/i386/ )
OS			:= $(shell uname -s )

PREFIX		:= $(dir $(word $(words $(MAKEFILE_LIST)), $(MAKEFILE_LIST)))



INCDIR		+= -I/home/stack/cloudexchange/vtn/OVSDBVtnDirect/SRC/wrap
INCDIR		+= -I/usr/include/mysql


LIBDIR		+= -L/home/stack/cloudexchange/vtn/OVSDBVtnDirect/SRC/wrap

LIBS		+= -lwrap -lmysqlclient_r -ldl

 
#
# 2009.03.02, with compile option
# 
CFLAGS		= -B$(PREFIX) -fPIC


LDFLAGS 	= $(LIBDIR) $(LIBS)

#
# 2009.03.02, alias for command
#
ifeq ("$(V)", "1")
	CC			= gcc
	CXX			= g++
	RM			= rm -f
	CP			= cp -f
	MV			= mv -f
	AR			= ar
	RANLIB		= ranlib
	PROC		= proc
else
	CC			= @echo "        CC      " $@; gcc
	CXX			= @echo "        CXX     " $@; g++
	RM			= @rm -f
	CP			= @cp -f
	MV			= @mv -f
	AR			= @echo "        AR      " $@; ar
	RANLIB		= @echo "        RANLIB  " $@; ranlib
	PROC		= @echo "		 PROC	 " $@; proc
endif

CHECKFLAGS		= -D__x86_64__ -m64 -D_MYSQL_

# edit by weawen 2011.10.20 15:55
# valgrind 테스트를 위한 optimization 레벨 조절
CFLAGS 			+= -O2
CPPFLAGS		+= -O2
#CFLAGS 			+= -O
#CPPFLAGS		+= -O

#
# 2009.03.02, with debugging options
#
CFLAGS 			+= -ggdb 


#
# 2009.03.02, add directory information
#
CFLAGS			+= $(INCDIR) $(CHECKFLAGS)
CXXFLAGS		= $(CFLAGS)
MAKEFLAGS 		+= --no-print-directory


ifneq (,$(findstring UTIL,$(CURDIR)))
    INSTALLDIR = $(HOME)/UTIL
    NETINSTALL_DIR = UTIL
endif

#
# 2009.03.02, suffix
#
.cpp.o:
	$(CXX) -c $(CXXFLAGS) $(LOCALFLAGS) -o $@ $<
.c.o:
	$(CC) -c $(CFLAGS) $(LOCALFLAGS) -o $@ $<
.S.o:
	$(AS) -c $(INCDIR) -o $@ $<
.s.o:
	$(AS) -c $(LIBDIR) -o $@ $<

.PHONY:	all clean install netinstall initial tags cscope distclean

all clean install netinstall initial tags cscope distclean ::
	@set -e;						\
	for i in $(SUBDIR); 			\
	do ( 							\
		if [ $$i"NULL" != "NULL" ];	\
		then 						\
			echo "    CD " $(CURDIR)/$$i;	\
			$(MAKE) -C $$i $@;		\
		fi 							\
	); 								\
	done;							\

clean ::
	@echo "        CLEAN   " $(CURDIR)
	$(RM) -f $(EXES) *.o *.gcov *.gcda *.gcno

tags ::
	ctags *.c *.h *.cpp *.hpp

cscope ::

distclean :: clean
	rm -f tags

install ::
	@set -e;									\
	if [ "NULL$(EXES)" != "NULL" ];				\
	then										\
		echo "        INSTALL $(EXES)";			\
		cp $(EXES) $(INSTALLDIR);				\
	fi											

