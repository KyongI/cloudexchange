/**
 * @file   nodes.h
 * @brief  nodes in the parse tree output by the parser 
 */

#ifndef _CONFIGS_
#define _CONFIGS_

#include <stdint.h>

#define DEF_MAX_CLIENT	200

typedef struct vm_config {
	char ip[40];
	char id[40];
	char pw[40];
} VM_CONF;

typedef struct config {
	VM_CONF	vm_config[10];
	uint8_t unDbCnt;
} CONFIG;

void init_config();
CONFIG *assign_vm1_ip_config(char *a_strIP);
CONFIG *assign_vm1_id_config(char *a_strID);
CONFIG *assign_vm1_pw_config(char *a_strPW);
CONFIG *assign_vm2_ip_config(char *a_strIP);
CONFIG *assign_vm2_id_config(char *a_strID);
CONFIG *assign_vm2_pw_config(char *a_strPW);
CONFIG *default_config();

#endif
