%{
/**
 * parser.y: yacc specification for CQL
 *
 * Contributors: 
 *           Mark McAuliffe (University of Wisconsin - Madison, 1991)
 *           Dallan Quass, Jan Jannink, Jason McHugh (for Redbase)
 *           Shivnath Babu, Arvind Arasu (for STREAM)
 *
 */

#include <stdio.h>
#include <iostream>
#include <assert.h>
#include <string.h>
#include "scan.h"
#include "parser.h"

static CONFIG* parse_tree; 


%}

%union{
  int   ival;
  float rval;
  char *sval;
  CONFIG* config;
}

%token NOTOKEN

%token CW_MASK
%token CW_CLIENT_COUNT
%token CW_CLIENT_CORE
%token CW_PORT_MASK
%token CW_NODE_COUNT
%token CW_HUGE_COUNT
%token CW_HUGE_SIZE
%token CW_DB_ADDR
%token CW_DB_USER
%token CW_DB_NAME
%token CW_DB_PASS
%token CW_SERVER_PORT
%token T_ASSIGN

%token <ival> T_INT
%token <rval> T_REAL
%token <sval> T_STRING
%token <sval> T_QSTRING

%left               '+' '-'
%left               '*' '/'

%type  <config> command
%type  <config> mask_config
%type  <config> client_count_config
%type  <config> port_mask_config
%type  <config> node_count_config
%type  <config> huge_count_config
%type  <config> huge_size_config
%type  <config> client_core_config
%type  <config> db_config
%type  <config> server_port_config

%%

start
   : command { parse_tree = $1; YYACCEPT; }   
   ;

command
   : mask_config
     {$$ = $1;}
    
   | client_count_config
     {$$ = $1;}

   | port_mask_config
     {$$ = $1;}

   | node_count_config
     {$$ = $1;}

   | huge_count_config
     {$$ = $1;}

   | huge_size_config 
     {$$ = $1;}

   | client_core_config
     {$$ = $1;}

   | db_config
     {$$ = $1;}

   | server_port_config
     {$$ = $1;}

   | nothing
     {$$ = default_config(); }

mask_config
   : CW_MASK T_ASSIGN T_STRING
     {$$ = assign_core_mask($3);}
   | CW_MASK T_ASSIGN T_INT
     {$$ = assign_core_mask($3);}
   ;


client_count_config
   : CW_CLIENT_COUNT T_ASSIGN T_INT
     {$$ = assign_client_count($3);}
   ;

port_mask_config
   : CW_PORT_MASK T_ASSIGN T_INT
     {$$ = assign_port_mask($3);}
   ;

node_count_config
   : CW_NODE_COUNT T_ASSIGN T_INT
     {$$ = assign_node_count($3);}
   ;

huge_count_config
   : CW_HUGE_COUNT T_ASSIGN T_INT
     {$$ = assign_huge_count($3);}
   ;

huge_size_config
   : CW_HUGE_SIZE T_ASSIGN T_STRING
     {$$ = assign_huge_size($3);}
   ;

client_core_config
   : CW_CLIENT_CORE T_INT T_ASSIGN T_INT
     {$$ = assign_client_core($2, $4);}
   ;

db_config
   : CW_DB_ADDR T_ASSIGN T_STRING
     {$$ = assign_db_addr($3);}
   | CW_DB_USER T_ASSIGN T_STRING
     {$$ = assign_db_user($3);}
   | CW_DB_PASS T_ASSIGN T_STRING
     {$$ = assign_db_pass($3);}
   | CW_DB_NAME T_ASSIGN T_STRING
     {$$ = assign_db_name($3);}
   ;

server_port_config
   : CW_SERVER_PORT T_ASSIGN T_INT
     {$$ = assign_server_port($3);}
   ;

nothing
   :
   ;

%%

using namespace Parser;

void Parser::parse_init_config()
{
  // Initialize the config pool
  init_config(); 

}

CONFIG* Parser::parseCommand(const char *queryBuffer, unsigned int queryLen) 
{
  int rc;

  // Initialize the scanner to scan the buffer
  init_scanner(queryBuffer, queryLen);  

  // Parse
  rc = yyparse();
    
  // Error parsing: return a null node
  if(rc != 0)
    return 0;
  
  // return the parse tree
  return parse_tree;  
}

void yyerror(char const *s) {
  printf("YYError: %s", s);
}

/*
int main(int argc, char *args[])
{
	printf("hi\n");
	CONFIG *p;
	p = NULL;
	p = parseCommand("name = lee.kim.a\n", strlen("name = lee.kim.a\n"));
	p = parseCommand("Mask = 0x7722\n", strlen("name = 0x7722\n"));
	p = parseCommand("client_count=30\n", strlen("client_count=30\n"));
	if(p != NULL)
	{
		printf("p name = %s\n", p->name);
		printf("p mask = %s\n", p->mask);
		printf("p client_cnt = %d\n", p->client);
	}
	return 0;
}



*/
