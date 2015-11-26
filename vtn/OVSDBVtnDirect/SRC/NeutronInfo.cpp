#include "NeutronInfo.hpp"

CNeutronInfo::CNeutronInfo()
{
	m_pcDbConnect_ =  NULL;
	m_pResult = NULL;

}

CNeutronInfo::~CNeutronInfo()
{

}

int CNeutronInfo::
Init(DbConnect* pcDbConnect) 
{
	m_pcDbConnect_ = pcDbConnect;
	return ITF_OK;
}

int CNeutronInfo::
GetNetworksInfo(std::vector<NeutronNetworks> &_vecNet, 
				char *_tbName,
				bool _vmode)
{
	printf("--- neutron::%s --------------------------------------------------\n", _tbName);

	int		count=0;
	int		nRowCount; 
#ifdef _PRINT_ALLROWS
	int		fields;
#endif
	char	query[1024];
	NeutronNetworks	nNetw;

	memset(query, 0x00, sizeof(query));
	snprintf(query, 1024, "select * from %s", _tbName);

	nRowCount = m_pcDbConnect_->ExecuteSQL((char *)query);
	if (nRowCount == ITF_ERROR)
	{
		printf(" Table [%s] info get failed\n", _tbName);
		return ITF_ERROR;
	}
	else if (nRowCount == 0) 
	{
		printf(" Table [%s] has no more rows\n\n", _tbName);
		return ITF_ERROR;
	}

	m_pResult = m_pcDbConnect_->GetDBRes();
#ifdef _PRINT_ALLROWS
	fields    = mysql_num_fields(m_pResult);
#endif

	while((row = mysql_fetch_row(m_pResult)))
	{
		memset(&nNetw, 0x00, sizeof(NeutronNetworks));

#ifdef _PRINT_ALLROWS
		for(int cnt = 0 ; cnt < fields ; ++cnt)
		{
			printf(" %s ||", row[cnt]);
		}
		printf("\n");
#endif
		unsigned int rowIdx = 0;

		strncpy(nNetw.tenant_id, row[rowIdx++], TENANT_ID_SIZE);
		strncpy(nNetw.id,        row[rowIdx++], ID_SIZE);

		if (_vmode == true)
		{
			printf(" %d:", count++);
			printf(" [TENANT_ID] "GREEN"%s "RESET"||", nNetw.tenant_id);
			printf(" [ID] "GREEN"%s "RESET"\n", nNetw.id);
		}

		_vecNet.push_back(nNetw);
	}

	if (_vmode == false) 
		printf(" TENANE_ID/ID get success\n\n");
	else
		printf("\n");

	return ITF_OK; 
}

int CNeutronInfo::
GetSubnetsInfo(std::vector<NeutronSubnets> &_vecSubn, 
			   char *_tbName,
			   bool _vmode)
{
	printf("--- neutron::%s --------------------------------------------------\n", _tbName);

	int		count=0;
	int		nRowCount;
#ifdef _PRINT_ALLROWS
	int		fields;
#endif
	char	query[1024];
	NeutronSubnets	nSubnet;

	memset(query, 0x00, sizeof(query));
	snprintf(query, 1024, "select * from %s", _tbName);

	nRowCount = m_pcDbConnect_->ExecuteSQL((char*)query);
	if (nRowCount == ITF_ERROR)
	{
		printf(" Table [%s] info get failed\n", _tbName);
		return ITF_ERROR;
	}
	else if (nRowCount == 0) 
	{
		printf(" Table [%s] has no more rows\n\n", _tbName);
		return ITF_ERROR;
	}

	m_pResult = m_pcDbConnect_->GetDBRes();
#ifdef _PRINT_ALLROWS
	fields    = mysql_num_fields(m_pResult);
#endif

	while((row = mysql_fetch_row(m_pResult)))
	{
		memset(&nSubnet, 0x00, sizeof(NeutronSubnets));

#ifdef _PRINT_ALLROWS
		for(int cnt = 0 ; cnt < fields ; ++cnt)
		{
			printf(" %s ||", row[cnt]);
		}
		printf("\n\n");
#endif
		unsigned int rowIdx = 0;

		strncpy(nSubnet.tenant_id,  row[rowIdx++], TENANT_ID_SIZE);
		rowIdx++;
		strncpy(nSubnet.name,       row[rowIdx++], NAME_SIZE);
		strncpy(nSubnet.network_id, row[rowIdx++], NET_ID_SIZE);

		if (_vmode == true)
		{
			printf(" %d:", count++);
			printf(" [TENANT_ID] "GREEN"%s "RESET"||", nSubnet.tenant_id);
			printf(" [NAME] "GREEN"%s "RESET"||\n", nSubnet.name);
			printf("    [NETWORK_ID] "GREEN"%s "RESET"\n", nSubnet.network_id);
		}

		_vecSubn.push_back(nSubnet);
	}

	if (_vmode == false) 
		printf(" TENANE_ID/NAME/NETWORK_ID get success\n\n");
	else
		printf("\n");

	return ITF_OK;
}

int CNeutronInfo::
GetPortsInfo(std::vector<NeutronPorts> &_vecPort, 
			 char *_tbName,
			 bool _vmode)
{
	printf("--- neutron::%s --------------------------------------------------\n", _tbName);

	int		count=0;
	int		nRowCount;
#ifdef _PRINT_ALLROWS
	int		fields;
#endif
	char	query[1024];
	NeutronPorts	nPorts;

	memset(query, 0x00, sizeof(query));
	snprintf(query, 1024, "select * from %s", _tbName);

	nRowCount = m_pcDbConnect_->ExecuteSQL((char*)query);
	if (nRowCount == ITF_ERROR)
	{
		printf(" Table [%s] info get failed\n", _tbName);
		return ITF_ERROR;
	}
	else if (nRowCount == 0) 
	{
		printf(" Table [%s] has no more rows\n\n", _tbName);
		return ITF_ERROR;
	}

	m_pResult = m_pcDbConnect_->GetDBRes();
#ifdef _PRINT_ALLROWS
	fields    = mysql_num_fields(m_pResult);
#endif

	while((row = mysql_fetch_row(m_pResult)))
	{
		memset(&nPorts, 0x00, sizeof(NeutronPorts));

#ifdef _PRINT_ALLROWS
		for(int cnt = 0 ; cnt < fields ; ++cnt)
		{
			printf(" %s ||", row[cnt]);
		}
		printf("\n");
#endif
		unsigned int rowIdx = 0;

		strncpy(nPorts.tenant_id,  row[rowIdx++], TENANT_ID_SIZE);
		strncpy(nPorts.id       ,  row[rowIdx++], ID_SIZE);
		rowIdx++;
		strncpy(nPorts.network_id, row[rowIdx++], NET_ID_SIZE);
		rowIdx += 3;
		strncpy(nPorts.device_id,  row[rowIdx++], DEVICE_ID_SIZE);

		if (_vmode == true)
		{
			printf(" %d:", count++);
			printf(" [ID] "GREEN"%s "RESET"||\n", nPorts.id);
			printf("    [TENANT_ID] "GREEN"%s "RESET"||", nPorts.tenant_id);
			printf(" [NETWORK_ID] "GREEN"%s "RESET"||\n", nPorts.network_id);
			printf("    [DEVICE_ID] "GREEN"%s "RESET"\n", nPorts.device_id);
		}

		_vecPort.push_back(nPorts);
	}

	if (_vmode == false) 
		printf(" TENANE_ID/ID/NETWORK_ID/DEVICE_ID get success\n\n");
	else
		printf("\n");

	return ITF_OK;
}

int CNeutronInfo::
ShowTableInfo(void)
{
	printf("--- neutron::table list --------------------------------------------------\n");

	int		nRowCount;
	int		fields;
	char	query[1024];

	memset(query, 0x00, sizeof(query));
	snprintf(query, 1024, "show tables");

	nRowCount = m_pcDbConnect_->ExecuteSQL((char*)query);
	if (nRowCount == ITF_ERROR)
	{
		printf(" Table info get failed\n\n");
		return ITF_ERROR;
	}
	else if (nRowCount == 0) 
	{
		printf(" Table has no more rows\n\n");
		return ITF_ERROR;
	}

	m_pResult = m_pcDbConnect_->GetDBRes();
	fields    = mysql_num_fields(m_pResult);

	while((row = mysql_fetch_row(m_pResult)))
	{
		for(int cnt = 0 ; cnt < fields ; ++cnt)
		{
			printf(" %s ||", row[cnt]);
		}
		printf("\n");
	}
	printf("\n");

	return ITF_OK;
}
