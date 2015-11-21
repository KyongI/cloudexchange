CXX = g++
LIBS = -ll
BISON = bison
LEX = lex
AR = ar
RANLIB = ranlib

OBJS = parse.o scan.o scanhelp.o config.o
PARSER_LIB = libparse.a

all : $(PARSER_LIB)

$(PARSER_LIB) : $(OBJS)
#	$(CXX) -o test_parser parse.tab.cc lex.yy.c scanhelp.c config.c $(LIBS)
	$(AR) cru $@ $^
	$(RANLIB) $@

.c.o :
	$(CXX) -c $< -o $@

parse.o : parse.tab.cc
	$(CXX) -c $< -o $@

scan.o : lex.yy.c
	$(CXX) -c $< -o $@

parse.tab.cc : parse.yy
#	$(BISON) parse.yy --defines=parse.h
	$(BISON) $< --defines=parse.h

lex.yy.c : scan.ll
#	$(LEX) scan.ll
	$(LEX) $<




clean :
	@rm -f $(OBJS) $(PARSER_LIB) parse.tab.cc lex.yy.c parse.h
