#include "OVSDBDirect.hpp"
#include "CWrap.hpp"

CWrap*		g_pcWrap;
CSingleLog*	g_pcLog;

COVSDBDirect::COVSDBDirect()
{
	m_unDbCnt = 0;
	m_pcPrint = NULL;

	for ( int i = 0; i < 10 ; i++ )
	{
		m_pcDbConnect_[i] = NULL;
	}

	m_nRet = 0;
	memset(m_szHost, 0x00, sizeof(m_szHost));
	memset(m_szUser, 0x00, sizeof(m_szUser));
	memset(m_szPass, 0x00, sizeof(m_szPass));
	memset(m_szDb,   0x00, sizeof(m_szDb));
}

COVSDBDirect::~COVSDBDirect()
{
	for (int i = 0; i < m_unDbCnt ; i++)
	{
		if ( m_pcDbConnect_[i] != NULL) 
		{
			delete m_pcDbConnect_[i];
		}
	}
}

int COVSDBDirect::Init(CONFIG *a_stConf_)
{
	int ret = 0;

	memset(m_pcDbConnect_, 0x00, sizeof(m_pcDbConnect_));

	m_unDbCnt = a_stConf_->unDbCnt;

	if (m_unDbCnt == 0)
	{
		g_pcLog->LogMsg(0, (char*)NULL, "Error, DB Count is Zero");
		return ITF_ERROR;
	}

	for (int i = 0; i < m_unDbCnt ; i++)
	{
		m_pcDbConnect_[i] = new DbConnect(&ret, 
										  a_stConf_->vm_config[i].ip, 
										  a_stConf_->vm_config[i].id, 
										  a_stConf_->vm_config[i].pw, 
										  NULL);
		ret = m_pcDbConnect_[i]->ConnectDB();
		if (ret != ITF_OK)
		{
			g_pcLog->LogMsg(0, (char*)NULL, 
							" DB Connect Failure : IP [%s] User [%s] Pw [%s]\n\n", 
							a_stConf_->vm_config[i].ip,
							a_stConf_->vm_config[i].id,
							a_stConf_->vm_config[i].pw);
			return ITF_ERROR;
		}
		else	
		{
			g_pcLog->LogMsg(0, (char*)NULL, 
							" DB Connect Success : IP [%s] User [%s] Pw [%s]\n\n", 
							a_stConf_->vm_config[i].ip,
							a_stConf_->vm_config[i].id, 
							a_stConf_->vm_config[i].pw);
		}
	}

	m_pcPrint = new PrintUtil();
	if (m_pcPrint != NULL)
	{
		m_pcPrint->Initialize();
	}

	return ITF_OK;
}

void COVSDBDirect::Usage(char *s)
{
	printf("\n\n=====================================================================\n");
	printf("\n");
	printf("                      Cloud Info Viewer V1.0 \n");
	printf("\n");
	printf("=====================================================================\n");
	printf("\n");
	printf("USAGE:\n");
	printf("  %s [-a] \n", s);
	printf("  %s [-d] {DB name}\n", s);
	printf("  %s [-t] {Table name}\n", s);
	printf("  %s [-k] {Keystone table name}\n", s);
	printf("  %s [-i] {DB name}\n", s);
	printf("\n");
	printf("DESCRIPTION:\n");
	printf("  This utility displays OpenStack DB information.\n");
	printf("  DB option is neutron,nova,keystone. Other DBs are not supported in this version .\n");
	printf("  Tables selection is also limited. List are as belows\n");
	printf("   - [NEUTRON]  networks, subnets, ports\n");
	printf("   - [NOVA]     certifcates, instances\n");
	printf("   - [KEYSTONE] endpoint, project, token\n");
	printf("\n");
	printf("OPTION:\n");
	printf("  h : Help output.\n");
	printf("  a : View all DB information\n");
	printf("  d : View selected DB information (ex. neutron, nova, keystone)\n");
	printf("  t : View selected table information (ex. networks, subnets, ports...)\n");
	printf("  k : View selected table's ID conversion (ex. endpoint, project, token)\n");
	printf("  i : View DB table list\n");
	printf("\n");
	printf("EXAMPLES:\n");
	printf("                                  Last Change : %s %s\n", __DATE__, __TIME__);
	printf("=====================================================================\n\n\n\n");
}

int COVSDBDirect::Run(int argc, char** argv)
{
	char	 cOption;
#if 0
	char cFileName[80];
	FILE *pFop;
	char *cLineSave;
	int  nFileCount = 0;
	int  nPrintFlag = 0;
#endif

	while ((cOption = getopt(argc, argv, "had:t:k:i:")) != -1 ){
		switch(cOption){
			case 'h':
				Usage(argv[0]);
				return ITF_OK;
			case 'a':
				ShowAllInfo();
				return ITF_OK;
			case 'd':
				ShowDBInfo(optarg);
				return ITF_OK;
			case 't':
				ShowTableInfo(optarg);
				return ITF_OK;
			case 'k':
				ShowKeyInfo(optarg);
				return ITF_OK;
			case 'i':
				ShowDBTableList(optarg);
				return ITF_OK;
			case '?':
				printf("Unknown option: %c\n", optopt);
				Usage(argv[0]);
				return ITF_OK;
			default :
				Usage(argv[0]);
				exit(0);
		}
	}

	Usage(argv[0]);
	
#if 0
	nFileCount = optind;

	for ( ; nFileCount <= argc -1 ; nFileCount++)
	{
		strcpy(cFileName, argv[nFileCount]);

		if ((pFop = fopen(cFileName,"r")) < 0) {
			printf("[LOG] INPUT FILE OPEN ERROR");
			return -1;
		}

		cLineSave = (char*)malloc(LINE_MAX_LENGTH);

		while(fgets(cLineSave, LINE_MAX_LENGTH, pFop))
		{
			printf("%s \n",cLineSave);
		}

		fclose(pFop);
		free(cLineSave);

	} // for ( ; nFileCount <= argc -1 ; nFileCount++)
#endif
	return ITF_OK;
} 

void COVSDBDirect::ShowAllInfo()
{
	for (int i = 0; i < m_unDbCnt ; i++)
	{
		m_pcPrint->PrintVM(i);
		m_pcPrint->PrintNeutronInfo(m_pcDbConnect_[i]);
		m_pcPrint->PrintNovaInfo(m_pcDbConnect_[i]);
		m_pcPrint->PrintEndpointInfo(m_pcDbConnect_[i], false);
		m_pcPrint->PrintProjectInfo(m_pcDbConnect_[i], false);
		m_pcPrint->PrintTokenInfo(m_pcDbConnect_[i], false);
	}
}

void COVSDBDirect::ShowTableInfo(char *_tbname)
{
	if (strcmp(optarg, "networks") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintNetworkInfo(m_pcDbConnect_[i]);
		}
	}
	else if (strcmp(optarg, "subnets") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintSubnetInfo(m_pcDbConnect_[i]);
		}
	}
	else if (strcmp(optarg, "ports") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintPortInfo(m_pcDbConnect_[i]);
		}
	}
	else if (strcmp(optarg, "certificates") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintCertificateInfo(m_pcDbConnect_[i]);
		}
	}
	else if (strcmp(optarg, "instances") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintInstanceInfo(m_pcDbConnect_[i]);
		}
	}
	else if (strcmp(optarg, "endpoint") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintEndpointInfo(m_pcDbConnect_[i]);
		}
	}
	else if (strcmp(optarg, "project") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintProjectInfo(m_pcDbConnect_[i]);
		}
	}
	else if (strcmp(optarg, "token") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintTokenInfo(m_pcDbConnect_[i]);
		}
	}
	else
	{
		printf(" Invalid table name. Select appropriate table name as below.\n");
		printf(" - [neutron DB] networks, subnets, ports\n");
		printf(" - [nova DB] certificates, instances\n");
		printf(" - [keystone DB] endpoint, project, token\n");
	}
}

void COVSDBDirect::ShowKeyInfo(char *_tbname)
{
	if (strcmp(optarg, "endpoint") == 0)
	{
		for (int i = 0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintEndpointInfo(m_pcDbConnect_[i], false);
		}
	}
	else if (strcmp(optarg, "project") == 0)
	{
		for (int i = 0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintProjectInfo(m_pcDbConnect_[i], false);
		}
	}
	else if (strcmp(optarg, "token") == 0)
	{
		for (int i = 0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintTokenInfo(m_pcDbConnect_[i], false);
		}
	}
	else
	{
		printf(" Invalid table name. Use \"endpoint\" or \"project\" or \"token\"\n");
	}
}

void COVSDBDirect::ShowDBInfo(char *_dbname)
{
	if (strcmp(optarg, "neutron") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintNeutronInfo(m_pcDbConnect_[i]);
		}
	}
	else if (strcmp(optarg, "nova") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintNovaInfo(m_pcDbConnect_[i]);
		}
	}
	else if (strcmp(optarg, "keystone") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintKeystoneInfo(m_pcDbConnect_[i]);
		}
	}
	else
	{
		printf(" Invalid DB name. Use \"neutron\" or \"nova\" or \"keystone\"\n");
	}
}

void COVSDBDirect::ShowDBTableList(char *_dbname)
{
	if (strcmp(optarg, "neutron") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintNeutronTablelist(m_pcDbConnect_[i]);
		}
	}
	else if (strcmp(optarg, "nova") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintNovaTablelist(m_pcDbConnect_[i]);
		}
	}
	else if (strcmp(optarg, "keystone") == 0)
	{
		for (int i=0; i < m_unDbCnt ; i++)
		{
			m_pcPrint->PrintVM(i);
			m_pcPrint->PrintKeystoneTablelist(m_pcDbConnect_[i]);
		}
	}
	else
	{
		printf(" Invalid DB name. Use \"neutron\" or \"nova\" or \"keystone\"\n");
	}
}

int main(int argc, char *argv[])
{
	COVSDBDirect clsOVSDB;
	CONFIG*		g_stConfig = NULL;

	g_pcWrap = NULL;
	g_pcWrap = new CWrap((char*)"OVS_LOG");

	g_pcWrap->Initialize();
	g_pcLog = g_pcWrap->GetLog();
	
	g_pcLog->LogMsg(0, (char*)NULL, "Info, Start UP");

	g_stConfig = g_pcWrap->GetConfig();

	if( clsOVSDB.Init(g_stConfig) == ITF_ERROR )
	{
		g_pcLog->LogMsg(0, (char*)NULL, "Error, Viewer Init() Error");
		exit(ITF_EXIT_ABNORMAL);
	}

#if 0
	PrintUtil *g_cPrint = NULL;
	g_cPrint = new PrintUtil();
	g_cPrint->PrintInstance();
#endif
	if (clsOVSDB.Run(argc, argv) != ITF_OK) 
		exit(ITF_EXIT_ABNORMAL);
	else 
		exit(ITF_EXIT_NORMAL);

	return ITF_OK;
}



