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

%token CW_VM1_IP
%token CW_VM1_ID
%token CW_VM1_PW
%token CW_VM2_IP
%token CW_VM2_ID
%token CW_VM2_PW
%token T_ASSIGN

%token <ival> T_INT
%token <rval> T_REAL
%token <sval> T_STRING
%token <sval> T_QSTRING

%left               '+' '-'
%left               '*' '/'

%type  <config> command
%type  <config> vm1_ip_config
%type  <config> vm1_id_config
%type  <config> vm1_pw_config
%type  <config> vm2_ip_config
%type  <config> vm2_id_config
%type  <config> vm2_pw_config

%%

start
   : command { parse_tree = $1; YYACCEPT; }   
   ;

command
   : vm1_ip_config 
     {$$ = $1;}
    
   | vm1_id_config
     {$$ = $1;}

   | vm1_pw_config
     {$$ = $1;}

   | vm2_ip_config
     {$$ = $1;}

   | vm2_id_config
     {$$ = $1;}

   | vm2_pw_config
     {$$ = $1;}


   | nothing
     {$$ = default_config(); }

vm1_ip_config
   : CW_VM1_IP T_ASSIGN T_STRING
     {$$ = assign_vm1_ip_config($3);}
   ;

vm1_id_config
   : CW_VM1_ID T_ASSIGN T_STRING
     {$$ = assign_vm1_id_config($3);}
   ;

vm1_pw_config
   : CW_VM1_PW T_ASSIGN T_STRING
     {$$ = assign_vm1_pw_config($3);}
   ;

vm2_ip_config
   : CW_VM2_IP T_ASSIGN T_STRING
     {$$ = assign_vm2_ip_config($3);}
   ;

vm2_id_config
   : CW_VM2_ID T_ASSIGN T_STRING
     {$$ = assign_vm2_id_config($3);}
   ;

vm2_pw_config
   : CW_VM2_PW T_ASSIGN T_STRING
     {$$ = assign_vm2_pw_config($3);}
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
