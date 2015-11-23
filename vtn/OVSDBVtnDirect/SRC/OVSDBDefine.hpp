#ifndef _OVSDBDEFINE_HPP_
#define _OVSDBDEFINE_HPP_

#define TENANT_ID_SIZE	255
#define ID_SIZE			36
#define NAME_SIZE		255
#define NET_ID_SIZE		36
#define DEVICE_ID_SIZE	255
#define USER_ID_SIZE	255
#define PROJECT_ID_SIZE	255
#define HOSTNAME_SIZE	255
#define UUID_SIZE		36

typedef struct
{
	char	tenant_id	[TENANT_ID_SIZE+1];
	char	id			[ID_SIZE+1];
} NeutronNetworks;

#define NEUTRON_NET_SIZE	sizeof(NeutronNetworks)

typedef struct
{
	char	tenant_id	[TENANT_ID_SIZE+1];
	char	name		[NAME_SIZE+1];
	char	network_id	[NET_ID_SIZE+1];
} NeutronSubnets;

#define NEUTRON_SUBNET_SIZE	sizeof(NeutronSubnets)

typedef struct
{
	char	tenant_id	[TENANT_ID_SIZE+1];
	char	id			[ID_SIZE+1];
	char	network_id	[NET_ID_SIZE+1];
	char	device_id	[DEVICE_ID_SIZE+1];
} NeutronPorts;

#define NEUTRON_PORT_SIZE	sizeof(NeutronPorts)

typedef struct
{
	char	user_id		[USER_ID_SIZE+1];
	char	project_id	[PROJECT_ID_SIZE+1];
} NovaCerti;

#define NOVA_CERTI_SIZE		sizeof(NovaCerti)

typedef struct
{
	char	user_id		[USER_ID_SIZE+1];
	char	hostname	[HOSTNAME_SIZE+1];
	char	uuid		[UUID_SIZE+1];
} NovaInstances;

#define NOVA_INSTANCE_SIZE	sizeof(NovaInstances)

#endif
