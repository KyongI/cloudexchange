include ../../include.mk

default : all

WRAP_LIB = libwrap.a

OBJS = CSingleLog.o CWrap.o

.PHONY: all clean distclean

all :: $(WRAP_LIB)

$(WRAP_LIB) : $(OBJS)
	$(AR) cur $@ $^
	$(RANLIB) $@

clean ::
	$(RM) -f $(WRAP_LIB) *.o 
