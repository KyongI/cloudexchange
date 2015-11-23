#ifndef __WRAP_HPP_
#include "CWrap.hpp"
#endif

using namespace Parser;

/*	Constructor
 *	Input : Process name
 *	true : CWrap, error: NULL
 */
CWrap::CWrap(char *proc)
{
	memset(m_strProc, 0x00, sizeof(m_strProc));
	sprintf(m_strProc, "%s", proc);
	bRun = true;
	m_pLog = NULL;
}

/*	Destructor
 *	Input : void
 *	true : NULL, Error : NULL
 */
CWrap::~CWrap()
{
	if(m_pLog);
		delete m_pLog;


}

/*	Initialize Log and Config
 *	Input : void
 *	true : 0, Error: -1
 */
int CWrap::Initialize()
{	
	char strLogPath[DEF_BUFFER_256];
	memset(strLogPath, 0x00, sizeof(strLogPath));
	sprintf(strLogPath, "./");
	
	m_pLog = new CSingleLog();
	
	if(m_pLog == NULL || !(m_pLog->Initialize(m_strProc, 0, (char*)strLogPath)) )
	{
		printf("CSingleLog Init Failed\n");
		return -1;
	}

	//Get Config Information
	m_pstConfig = InitConfig();	

	if(m_pstConfig == NULL)
	{
		m_pLog->LogMsg(0, (char*)NULL, "Error, Config Load Failed");
		return -1;
	}

	return 0;
}

/*	Load Config from File
 *	input : void	
 *	true : 0, error: -1
 */
CONFIG* CWrap::InitConfig()
{
	//Config Pointer
	CONFIG *cfg = NULL;

	//Config File Pointer
	FILE *fp;

	//file Read Buffer
	char buff[DEF_BUFFER_1024];
	
	//Config File Path
	char strCfgPath[DEF_BUFFER_256];
	
	memset(strCfgPath, 0x00, sizeof(strCfgPath));
	sprintf(strCfgPath, "./OVS_CONFIG.cfg");

	fp = fopen(strCfgPath, "r");
	if(fp == NULL)
	{
		m_pLog->LogMsg(0, (char*)NULL, "Error, Config File Open Failed (%s)", strCfgPath);
		return NULL;
	}


	parse_init_config();
	
	//config Parsing use Parser Lib
	while(1)
	{
		memset(buff, 0x00, sizeof(buff));
		if(fgets(buff, sizeof(buff), fp) == NULL)
		{
			break;
		}
	
		cfg = parseCommand(buff, strlen(buff) );
	}


	return cfg;
}

