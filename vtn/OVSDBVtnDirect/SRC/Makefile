include ../makehead.mk

LOCALFLAGS = -I./ -D_CV_DATA_ 

EXE = UT_VI_OVSDB
OBS = 	OVSDBDirect.o \
		DbConnect.o

all : $(EXE)

$(EXE) : $(OBJS)
	$(CC) -o $@ $(OBJS) $(CFLAGS) $(PROLDLIBS) $(MDDB_LIB) $(MDCOMM_LIB) $(COMM_LIB) $(USER_LIB) $(DB_OBJ) $(LFLAGS)

install : $(EXE)
	$(MV) $(EXE) $(UTILPATH)/

clean :
	rm -rf $(EXE) $(OBJS) core.*
