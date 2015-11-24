#include "OVSDBDirect.hpp"
#include "CWrap.hpp"

using namespace Parser;

CWrap*		g_pcWrap;
CSingleLog*	g_pcLog;

COVSDBDirect::COVSDBDirect()
{
	m_unDbCnt = 0;
	m_pcPrint = NULL;
}

COVSDBDirect::~COVSDBDirect()
{
	for(int i = 0; i < m_unDbCnt ; i++)
	{
		if( m_pcDbConnect_[i] != NULL) {
			delete m_pcDbConnect_[i];
		}
	}
}

int COVSDBDirect::Init(CONFIG *a_stConf_)
{
	int ret = 0;

	memset(m_pcDbConnect_, 0x00, sizeof(m_pcDbConnect_));

	m_unDbCnt = a_stConf_->unDbCnt;

	if(m_unDbCnt == 0)
	{
		g_pcLog->LogMsg(0, (char*)NULL, "Error, DB Count is Zero");
		return ITF_ERROR;
	}

	for(int i = 0; i < m_unDbCnt ; i++)
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
	if(m_pcPrint != NULL)
	{
		m_pcPrint->Initialize();
	}

//	m_pcNeutronInfo_	= new CNeutronInfo();
//	m_pcNovaInfo_		= new CNovaInfo();
	m_pcKeystoneInfo_   = new CKeystoneInfo();

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
	printf("  %s [-d] {DB name}\n", s);
	printf("  %s [-t] {Table name}\n", s);
	printf("  %s [-k] {Keystone table name}\n", s);
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
	printf("  d : View selected DB information (ex. neutron, nova, keystone)\n");
	printf("  t : View selected table information (ex. networks, subnets, ports...)\n");
	printf("  k : View selected table's ID conversion (ex. endpoint, project, token)\n");
	printf("  a : View all DB information\n");
	printf("\n");
	printf("EXAMPLES:\n");
	printf("                                  Last Change : %s %s\n", __DATE__, __TIME__);
	printf("=====================================================================\n\n\n\n");
}

int COVSDBDirect::Run(int argc, char** argv)
{
	char	 cOption;
	char	*dbname;
#if 0
	char cFileName[80];
	FILE *pFop;
	char *cLineSave;
	int  nFileCount = 0;
	int  nPrintFlag = 0;
#endif

	while ((cOption = getopt(argc, argv, "had:t:k:")) != -1 ){
		switch(cOption){
			case 'h':
				Usage(argv[0]);
				return ITF_OK;
			case 'd':
				dbname = optarg;
				if (strcmp(optarg, "neutron") == 0)
				{
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintNeutronInfo(m_pcDbConnect_[i]);
					}
				}
				else if (strcmp(optarg, "nova") == 0)
				{
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintNovaInfo(m_pcDbConnect_[i]);
					}
				}
				else if (strcmp(optarg, "keystone") == 0)
				{
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintKeystoneInfo(m_pcDbConnect_[i]);
					}
				}
				else
				{
					printf(" Invalid DB name. Use \"neutron\" or \"nova\"\n");
				}
				return ITF_OK;
			case 't':
				if (strcmp(optarg, "networks") == 0)
				{
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintNetworkInfo(m_pcDbConnect_[i]);
					}
				}
				else if (strcmp(optarg, "subnets") == 0)
				{
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintSubnetInfo(m_pcDbConnect_[i]);
					}
				}
				else if (strcmp(optarg, "ports") == 0)
				{
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintPortInfo(m_pcDbConnect_[i]);
					}
				}
				else if (strcmp(optarg, "certificates") == 0)
				{
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintCertificateInfo(m_pcDbConnect_[i]);
					}
				}
				else if (strcmp(optarg, "instances") == 0)
				{
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintInstanceInfo(m_pcDbConnect_[i]);
					}
				}
				else if (strcmp(optarg, "endpoint") == 0)
				{
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintEndpointInfo(m_pcDbConnect_[i]);
					}
				}
				else if (strcmp(optarg, "project") == 0)
				{
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintProjectInfo(m_pcDbConnect_[i]);
					}
				}
				else if (strcmp(optarg, "token") == 0)
				{
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintTokenInfo(m_pcDbConnect_[i]);
					}
				}
				else
				{
					printf(" Invalid table name.\n");
					printf("  [table name list]\n");
					printf("   - networks, subnets, ports\n");
					printf("   - certificates, instances\n");
					printf("   - endpoint, project, token\n");
				}
				return ITF_OK;
			case 'a':
				for(int i = 0; i < m_unDbCnt ; i++)
				{
					m_pcPrint->PrintVM(i);
					m_pcPrint->PrintNeutronInfo(m_pcDbConnect_[i]);
					m_pcPrint->PrintNovaInfo(m_pcDbConnect_[i]);
					m_pcPrint->PrintEndpointInfo(m_pcDbConnect_[i], false);
					m_pcPrint->PrintProjectInfo(m_pcDbConnect_[i], false);
					m_pcPrint->PrintTokenInfo(m_pcDbConnect_[i], false);
				}
				return ITF_OK;
			case 'k':
				if (strcmp(optarg, "endpoint") == 0)
				{
					stdEndp_.clear();
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintEndpointInfo(m_pcDbConnect_[i], false);
					}
				}
				else if (strcmp(optarg, "project") == 0)
				{
					stdProj_.clear();
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintProjectInfo(m_pcDbConnect_[i], false);
					}
				}
				else if (strcmp(optarg, "token") == 0)
				{
					stdToken_.clear();
					for(int i = 0; i < m_unDbCnt ; i++)
					{
						m_pcPrint->PrintVM(i);
						m_pcPrint->PrintTokenInfo(m_pcDbConnect_[i], false);
					}
				}
				else
				{
					printf(" Invalid DB name. Use \"endpoint\" or \"project\" or \"token\"\n");
				}
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
	m_pcNeutronInfo_->Init(m_pcDbConnect_);
	m_pcNeutronInfo_->GetNetworksInfo(stdNetwork, (char*)"networks", false);
	m_pcNeutronInfo_->GetSubnetsInfo (stdSubnets, (char*)"subnets", false);
	m_pcNeutronInfo_->GetPortsInfo   (stdPorts,   (char*)"ports", false);
	m_pcNeutronInfo_->GetDBInfo ((char *)"routers");

	m_pcDbConnect_->SelectDB((char*)"nova");

	m_pcNovaInfo_->Init(m_pcDbConnect_);
	m_pcNovaInfo_->GetCertificatesInfo(stdCerts, (char*)"certificates", false);
	m_pcNovaInfo_->GetInstancesInfo   (stdInst,  (char*)"instances", false);

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
	if( clsOVSDB.Run(argc, argv) != ITF_OK ) exit(ITF_EXIT_ABNORMAL);
	else exit(ITF_EXIT_NORMAL);

	return ITF_OK;
}



