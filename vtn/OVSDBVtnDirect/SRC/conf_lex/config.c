#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "scan.h"
#include "config.h"

using namespace Parser;
using namespace std;


CONFIG configpool;

void init_config(void)
{
	memset(&configpool, 0x00, sizeof(CONFIG) );
	memset(configpool.client_core, -1, sizeof(configpool.client_core));
}

CONFIG* assign_core_mask(char *mask)
{
	sprintf(configpool.core_mask, "%s", mask);

	return &configpool;
}

CONFIG* assign_core_mask(int mask)
{
	sprintf(configpool.core_mask, "%d", mask);

	return &configpool;
}

CONFIG* assign_client_count(int cnt)
{
	configpool.client_count = cnt;

	return &configpool;

}

CONFIG* assign_port_mask(int mask)
{
	configpool.port_mask = mask;

	return &configpool;

}

CONFIG* assign_node_count(int cnt)
{
	configpool.node_count = cnt;

	return &configpool;

}

CONFIG* assign_huge_count(int cnt)
{
	configpool.huge_count = cnt;

	return &configpool;

}

CONFIG* assign_huge_size(char* size)
{
	if( !strcmp(size, "1GB") )
		configpool.huge_size = 1*1024*1024*1024;
	if( !strcmp(size, "2MB") )
		configpool.huge_size = 2*1024*1024;

	return &configpool;

}

CONFIG* assign_client_core(int clt_num, int core_num)
{
	if(clt_num-1 > DEF_MAX_CLIENT )
		return &configpool;

	if(clt_num-1 < 0 )
		return &configpool;

	configpool.client_core[clt_num-1] = core_num;

	return &configpool;
}

CONFIG* assign_db_addr( char *addr )
{
	sprintf(configpool.db_addr, "%s", addr);
	return &configpool;
}

CONFIG* assign_db_user( char *user )
{
	sprintf(configpool.db_user, "%s", user);
	return &configpool;
}

CONFIG* assign_db_pass( char *pass )
{
	sprintf(configpool.db_pass, "%s", pass); return &configpool;
}

CONFIG* assign_db_name( char *name )
{
	sprintf(configpool.db_name, "%s", name);
	return &configpool;
}

CONFIG* assign_server_port( int ser_port )
{
	configpool.server_port = ser_port;
	return &configpool;
}

CONFIG* default_config()
{
	return &configpool;
}



