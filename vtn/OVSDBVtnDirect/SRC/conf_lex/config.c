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
}

CONFIG* assign_vm1_ip_config(char *a_strIP)
{
	sprintf(configpool.vm_config[0].ip, "%s", a_strIP);
	configpool.unDbCnt++;

	return &configpool;
}

CONFIG* assign_vm1_id_config(char *a_strID)
{
	sprintf(configpool.vm_config[0].id, "%s", a_strID);

	return &configpool;
}

CONFIG* assign_vm1_pw_config(char *a_strPW)
{
	sprintf(configpool.vm_config[0].pw, "%s", a_strPW);

	return &configpool;

}

CONFIG* assign_vm2_ip_config(char *a_strIP)
{
	sprintf(configpool.vm_config[1].ip, "%s", a_strIP);
	configpool.unDbCnt++;

	return &configpool;
}

CONFIG* assign_vm2_id_config(char *a_strID)
{
	sprintf(configpool.vm_config[1].id, "%s", a_strID);

	return &configpool;
}

CONFIG* assign_vm2_pw_config(char *a_strPW)
{
	sprintf(configpool.vm_config[1].pw, "%s", a_strPW);

	return &configpool;

}

CONFIG* default_config()
{
	return &configpool;
}



