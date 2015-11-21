/**
 * @file   nodes.h
 * @brief  nodes in the parse tree output by the parser 
 */

#ifndef _CONFIGS_
#define _CONFIGS_

#include <stdint.h>

#define DEF_MAX_CLIENT	200

typedef struct config {
	char db_addr[30];
	char db_user[20];
	char db_pass[20];
	char db_name[20];
	char core_mask[20];
	uint16_t port_mask;
	uint16_t server_port;
	uint16_t client_count;
	uint16_t node_count;
	uint16_t huge_count;
	uint32_t huge_size;
	int client_core[DEF_MAX_CLIENT];
} CONFIG;

void init_config();
CONFIG *assign_client_count(int cnt);
CONFIG *assign_node_count(int cnt);
CONFIG *assign_huge_count(int cnt);
CONFIG *assign_huge_size(char *size);
CONFIG *assign_port_mask(char *mask);
CONFIG *assign_port_mask(int mask);
CONFIG *assign_core_mask(char *mask);
CONFIG *assign_core_mask(int mask);
CONFIG *assign_client_core(int clt_num, int core_num);
CONFIG* assign_db_addr( char *addr );
CONFIG* assign_db_user( char *user );
CONFIG* assign_db_pass( char *pass );
CONFIG* assign_db_name( char *name );
CONFIG* assign_server_port( int ser_port );
CONFIG *default_config();

#endif
