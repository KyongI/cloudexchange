#g++ test.cpp -I/usr/include/mysql -L/usr/lib64/mysql/ -lmysqlclient_r
include ../include.mk
LOCALFLAGS = -I./ -I./conf_lex -I./wrap -D_CV_DATA_ -L/usr/lib64/mysql/
EXE = UT_VI_OVSDB
OBJS = OVSDBDirect.o \
		DbConnect.o \
		NeutronInfo.o \
		NovaInfo.o \
		PrintUtil.o

SUBDIR = conf_lex \
	wrap

all :: $(EXE)

$(EXE) : $(OBJS)
	$(CXX) -o $@ $(OBJS) $(CFLAGS) $(INCDIR) $(LDFLAGS) -lparse

install :: $(EXE)
	$(MV) $(EXE) $(UTILPATH)/

clean ::
	rm -rf $(EXE) $(OBJS) core.
