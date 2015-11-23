#include "NovaInfo.hpp"

CNovaInfo::CNovaInfo()
{

}

CNovaInfo::~CNovaInfo()
{

}

int CNovaInfo::Init(DbConnect* pcDbConnect) 
{
	m_pcDbConnect_ = pcDbConnect;
	return ITF_OK;
}

int CNovaInfo::GetCertificatesInfo(std::vector<NovaCerti> &_vecCert, 
                                   char *_tbName,
                                   bool _vmode)
{
	printf("--- nova::%s --------------------------------------------------\n", _tbName);

	int		count=0;
	int		nRowCount; 
	int		fields;
	char	query[1024];
	NovaCerti	nCert;

	memset(query, 0x00, sizeof(query));
	sprintf(query, "select * from %s", _tbName);

	nRowCount = m_pcDbConnect_->ExecuteSQL((char *)query);
	if (nRowCount == ITF_ERROR)
	{
		printf(" Table [%s] info get failed\n\n", _tbName);
		return ITF_ERROR;
	}
	else if (nRowCount == 0)
	{
		printf(" Table [%s] has no more rows\n\n", _tbName);
		return ITF_ERROR;
	}

	m_pResult = m_pcDbConnect_->GetDBRes();
	fields    = mysql_num_fields(m_pResult);

	while((row = mysql_fetch_row(m_pResult)))
	{
		memset(&nCert, 0x00, sizeof(NovaCerti));

#ifdef _PRINT_ALLROWS
		for(int cnt = 0 ; cnt < fields ; ++cnt)
		{
			printf(" %s ||", row[cnt]);
		}
		printf("\n");
#endif
		unsigned int rowIdx = 0;

		rowIdx += 4;
		strncpy(nCert.user_id,    row[rowIdx++], USER_ID_SIZE);
		strncpy(nCert.project_id, row[rowIdx++], PROJECT_ID_SIZE);

		if (_vmode == true)
		{
			printf(" %d:", count++);
			printf(" [USER_ID] "YELLOW"%s "RESET"||", nCert.user_id);
			printf(" [PROJECT_ID] "YELLOW"%s "RESET"\n", nCert.project_id);
		}

		_vecCert.push_back(nCert);
	}

	if (_vmode == false)
		printf(" USER_ID/PROJECT_ID get success\n");
	else
		printf("\n");

	return ITF_OK; 
}

int CNovaInfo::GetInstancesInfo(std::vector<NovaInstances> &_vecInst, 
                                char *_tbName,
                                bool _vmode)
{
	printf("--- nova::%s --------------------------------------------------\n", _tbName);

	int		count=0;
	int		nRowCount;
	int		fields;
	char	query[1024];
	NovaInstances	nInst;

	memset(query, 0x00, sizeof(query));
	sprintf(query, "select * from %s", _tbName);

	nRowCount = m_pcDbConnect_->ExecuteSQL((char*)query);
	if (nRowCount == ITF_ERROR)
	{
		printf(" Table [%s] info get failed\n\n", _tbName);
		return ITF_ERROR;
	}
	else if (nRowCount == 0)
	{
		printf(" Table [%s] has no more rows\n\n", _tbName);
		return ITF_ERROR;
	}

	m_pResult = m_pcDbConnect_->GetDBRes();
	fields    = mysql_num_fields(m_pResult);

	while((row = mysql_fetch_row(m_pResult)))
	{
		memset(&nInst, 0x00, sizeof(NovaInstances));

#ifdef _PRINT_ALLROWS
		for(int cnt = 0 ; cnt < fields ; ++cnt)
		{
			printf(" %s ||", row[cnt]);
		}
		printf("\n");
#endif
		unsigned int rowIdx = 0;

		rowIdx += 5;
		strncpy(nInst.user_id,  row[rowIdx++], USER_ID_SIZE);
		strncpy(nInst.hostname, row[rowIdx++], HOSTNAME_SIZE);
		strncpy(nInst.uuid,     row[rowIdx++], UUID_SIZE);

		if (_vmode == true)
		{
			printf(" %d:", count++);
			printf(" [USER_ID] "GREEN"%s "RESET"||", nInst.user_id);
			printf(" [HOSTNAME] "GREEN"%s "RESET"||\n", nInst.hostname);
			printf("    [UUID] "GREEN"%s "RESET"\n", nInst.uuid);
		}
	}

	if (_vmode == false)
		printf(" USER_ID/HOSTNAME/UUID get success\n");
	else
		printf("\n");

	return ITF_OK;
}

int CNovaInfo::GetDBInfo(char *_tbName)
{
	printf("--- nova::%s --------------------------------------------------\n", _tbName);

	int		nRowCount;
	int		fields;
	char	query[1024];

	memset(query, 0x00, sizeof(query));
	sprintf(query, "select * from %s", _tbName);

	nRowCount = m_pcDbConnect_->ExecuteSQL((char*)query);
	if (nRowCount == ITF_ERROR)
	{
		printf(" Table [%s] info get failed\n\n", _tbName);
		return ITF_ERROR;
	}
	else if (nRowCount == 0)
	{
		printf(" Table [%s] has no more rows\n\n", _tbName);
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

int CNovaInfo::ShowTableInfo(void)
{
	printf("--- nova::table list --------------------------------------------------\n");

	int     nRowCount;
	int     fields;
	char    query[1024];

	memset(query, 0x00, sizeof(query));
	sprintf(query, "show tables");

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
