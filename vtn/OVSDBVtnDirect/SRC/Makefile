include ../makehead.mk
LOCALFLAGS = -I./ -D_CV_DATA_ 
EXE = UT_VI_OVSDB
OBJS = OVSDBDirect.o DbConnect.o

all:$(EXE)
$(EXE) : $(OBJS)
	$(CC) -o $@ $(OBJS) $(CFLAGS) $(DB_OBJ) $(LFLAGS)

install : $(EXE)
	$(MV) $(EXE) $(UTILPATH)/

clean :
	rm -rf $(EXE) $(OBJS) core.
