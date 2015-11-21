#ifndef _PARSER_
#define _PARSER_

#include "config.h"
namespace Parser {
	void parse_init_config();
	CONFIG *parseCommand(const char *queryBuffer, unsigned int queryLen);
}

#endif
