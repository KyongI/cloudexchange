#g++ test.cpp -I/usr/include/mysql -L/usr/lib64/mysql/ -lmysqlclient_r
include ../makehead.mk
LOCALFLAGS = -I./ -D_CV_DATA_ -L/usr/lib64/mysql/
EXE = UT_VI_OVSDB
OBJS = OVSDBDirect.o DbConnect.o

all:$(EXE)
$(EXE) : $(OBJS)
	$(CC) -o $@ $(OBJS) $(CFLAGS) $(LOCALFLAGS) $(DB_OBJ) $(LFLAGS)

install : $(EXE)
	$(MV) $(EXE) $(UTILPATH)/

clean :
	rm -rf $(EXE) $(OBJS) core.
