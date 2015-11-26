#g++ test.cpp -I/usr/include/mysql -L/usr/lib64/mysql/ -lmysqlclient_r
include ../include.mk
LOCALFLAGS = -I./ -I./wrap -D_CV_DATA_ -L/usr/lib64/mysql/
EXE = UT_VI_OVSDB
OBJS = OVSDBDirect.o \
		DbConnect.o \
		NeutronInfo.o \
		NovaInfo.o \
		KeystoneInfo.o \
		PrintUtil.o

SUBDIR = wrap

all :: $(EXE)

$(EXE) : $(OBJS)
	$(CXX) -o $@ $(OBJS) $(CFLAGS) $(INCDIR) $(LDFLAGS) 

install :: $(EXE)
	$(MV) $(EXE) $(UTILPATH)/

clean ::
	rm -rf $(EXE) $(OBJS) core.
