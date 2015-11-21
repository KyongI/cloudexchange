/*
 * scanhelp.c: help functions for lexer
 *
 * Authors: Jan Jannink 
 *          Jason McHugh
 *          
 * originally by: Mark McAuliffe, University of Wisconsin - Madison, 1991
 * 
 * 1997 Changes: "print", "buffer", "reset" and "io" added.
 * 1998 Changes: "resize", "queryplans", "on" and "off" added.
 *
 *
 * This file is not compiled separately; it is #included into lex.yy.c .
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "config.h"
#include "scan.h"
#include "parse.h"

/*
 * size of buffer of strings
 */
#define MAXCHAR		  5000
#define MAXSTRINGLEN   256

/*
 * buffer for string allocation
 */
static char charpool[MAXCHAR];
static int charptr = 0;

static int lower(char *dst, char *src, int max);
static char *mk_string(char *s, int len);

/*
 * string_alloc: returns a pointer to a string of length len if possible
 */
static char *string_alloc(int len)
{
	char *s;

	if(charptr + len > MAXCHAR){
		fprintf(stderr, "out of memory\n");
		exit(1);
	}

	s = charpool + charptr;
	charptr += len;

	return s;
}

/*
 * reset_charptr: releases all memory allocated in preparation for the
 * next query.
 *
 * No return value.
 */
void Parser::reset_charptr(void)
{
    charptr = 0;
}

/*
 * get_id: determines whether s is a reserved word, and returns the
 * appropriate token value if it is.  Otherwise, it returns the token
 * value corresponding to a string.  If s is longer than the maximum token
 * length (MAXSTRINGLEN) then it returns NOTOKEN, so that the parser will
 * flag an error (this is a stupid kludge).
 */
int Parser::get_id(char *s)
{
	static char string[MAXSTRINGLEN];
	int len;
	
	if((len = lower(string, s, MAXSTRINGLEN)) == MAXSTRINGLEN)
		return NOTOKEN;
	
	if(!strcmp(string, "core_mask"))
		return CW_MASK; 
	if(!strcmp(string, "client_count"))
		return CW_CLIENT_COUNT; 
	if(!strcmp(string, "port_mask"))
		return CW_PORT_MASK; 
	if(!strcmp(string, "node_count"))
		return CW_NODE_COUNT; 
	if(!strcmp(string, "hugepage_count"))
		return CW_HUGE_COUNT; 
	if(!strcmp(string, "hugepage_size"))
		return CW_HUGE_SIZE; 
	if(!strcmp(string, "client_core"))
		return CW_CLIENT_CORE; 
	if(!strcmp(string, "db_addr"))
		return CW_DB_ADDR; 
	if(!strcmp(string, "db_user"))
		return CW_DB_USER; 
	if(!strcmp(string, "db_name"))
		return CW_DB_NAME; 
	if(!strcmp(string, "db_pass"))
		return CW_DB_PASS; 
	if(!strcmp(string, "server_port"))
		return CW_SERVER_PORT; 
	
	/*  unresolved lexemes are strings */
	yylval.sval = mk_string(s, len);
	return T_STRING;
}

/*
 * lower: copies src to dst, converting it to lowercase, stopping at the
 * end of src or after max characters.
 *
 * Returns:
 * 	the length of dst (which may be less than the length of src, if
 * 	    src is too long).
 */
static int lower(char *dst, char *src, int max)
{
	int len;

	for(len = 0; len < max && src[len] != '\0'; ++len){
		dst[len] = src[len];
		if(src[len] >= 'A' && src[len] <= 'Z')
			dst[len] += 'a' - 'A';
	}
	dst[len] = '\0';

	return len;
}

/*
 * get_qstring: removes the quotes from a quoted string, allocates
 * space for the resulting string.
 *
 * Returns:
 * 	a pointer to the new string
 */
char *Parser::get_qstring(char *qstring, int len)
{
	/* replace ending quote with \0 */
	qstring[len - 1] = '\0';

	/* copy everything following beginning quote */
	return mk_string(qstring + 1, len - 2);
}

/*
 * mk_string: allocates space for a string of length len and copies s into
 * it.
 *
 * Returns:
 * 	a pointer to the new string
 */
static char *mk_string(char *s, int len)
{
	char *copy;

	/* allocate space for new string */
	if((copy = string_alloc(len + 1)) == NULL){
		printf("out of string space\n");
		exit(1);
	}
   
	/* copy the string */
	strncpy(copy, s, len + 1);
	return copy;
}

