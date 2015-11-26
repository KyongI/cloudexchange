#ifndef __WRAP_HPP_
#include "CWrap.hpp"
#endif


/*	Constructor
 *	Input : Process name
 *	true : CWrap, error: NULL
 */
CWrap::CWrap(char *proc)
{
	memset(m_strProc, 0x00, sizeof(m_strProc));
	snprintf(m_strProc, 20, "%s", proc);
	bRun = true;
	m_pLog = NULL;
	m_pstConfig = NULL;
}

/*	Destructor
 *	Input : void
 *	true : NULL, Error : NULL
 */
CWrap::~CWrap()
{
	if(m_pLog)
		delete m_pLog;
	if(m_pstConfig)
		delete m_pstConfig;

}

/*	Initialize Log and Config
 *	Input : void
 *	true : 0, Error: -1
 */
int CWrap::Initialize()
{	
	char strLogPath[DEF_BUFFER_256];
	memset(strLogPath, 0x00, sizeof(strLogPath));
	snprintf(strLogPath, DEF_BUFFER_256, "./");
	
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
	int nCfgNum = 0;
	//Config Pointer
	CONFIG *cfg = new CONFIG;
	if(cfg != NULL)
	{
		memset(cfg->vm_config,  0x00, sizeof(VM_CONF) * DEF_MAX_CONFIG);
		cfg->unDbCnt = 0;
	}

	//Config File Pointer
	FILE *fp;

	//file Read Buffer
	char buff[DEF_BUFFER_1024];
	char *p = NULL;
	
	//Config File Path
	char strCfgPath[DEF_BUFFER_256];
	
	memset(strCfgPath, 0x00, sizeof(strCfgPath));
	snprintf(strCfgPath, DEF_BUFFER_256, "./OVS_CONFIG.cfg");

	fp = fopen(strCfgPath, "r");
	if(fp == NULL)
	{
		m_pLog->LogMsg(0, (char*)NULL, "Error, Config File Open Failed (%s)", strCfgPath);
		delete cfg;
		return NULL;
	}


	//config Parsing use Parser Lib
	while(1)
	{
		memset(buff, 0x00, sizeof(buff));
		if(fgets(buff, sizeof(buff), fp) == NULL)
		{
			break;
		}
	
		p = buff;
		while(*(++p) != '\n')
		{
		}
		*p = 0x00;

		if( strncmp(buff, (char*)"VM_IP_", strlen( (char*)"VM_IP_" ) ) == 0)
		{
			nCfgNum = atoi( &(buff[6]) );
			if(nCfgNum >= DEF_MAX_CONFIG)
			{
				m_pLog->LogMsg(0, (char*)NULL, "Error, Max Config Count Over (%s) Max %d", buff, DEF_MAX_CONFIG);
				continue;
			}

			if(nCfgNum >= cfg->unDbCnt)
				cfg->unDbCnt = nCfgNum;

			p = &buff[8];
			while( (*p == ' ') || (*p == '=') )
			{
				p++;
			}
			
			sprintf(cfg->vm_config[nCfgNum-1].ip, "%s", p);
			m_pLog->LogMsg(0, (char*)NULL, "Info, cfg->vm_config[%d].ip (%s) ", nCfgNum, cfg->vm_config[nCfgNum].ip);
		}
		else if( strncmp(buff, (char*)"VM_ID_", strlen( (char*)"VM_ID_" ) ) == 0)
		{
			nCfgNum = atoi( &(buff[6]) );
			if(nCfgNum >= DEF_MAX_CONFIG)
			{
				m_pLog->LogMsg(0, (char*)NULL, "Error, Max Config Count Over (%s) Max %d", buff, DEF_MAX_CONFIG);
				continue;
			}

			if(nCfgNum >= cfg->unDbCnt)
				cfg->unDbCnt = nCfgNum;

			p = &buff[8];
			while( (*p == ' ') || (*p == '=') )
			{
				p++;
			}
			
			sprintf(cfg->vm_config[nCfgNum-1].id, "%s", p);
			m_pLog->LogMsg(0, (char*)NULL, "Info, cfg->vm_config[%d].id (%s) ", nCfgNum, cfg->vm_config[nCfgNum].id);
		}
		else if( strncmp(buff, (char*)"VM_PW_", strlen( (char*)"VM_PW_" ) ) == 0)
		{
			nCfgNum = atoi( &(buff[6]) );
			if(nCfgNum >= DEF_MAX_CONFIG)
			{
				m_pLog->LogMsg(0, (char*)NULL, "Error, Max Config Count Over (%s) Max %d", buff, DEF_MAX_CONFIG);
				continue;
			}

			if(nCfgNum >= cfg->unDbCnt)
				cfg->unDbCnt = nCfgNum;

			p = &buff[8];
			while( (*p == ' ') || (*p == '=') )
			{
				p++;
			}
			
			sprintf(cfg->vm_config[nCfgNum-1].pw, "%s", p);
			m_pLog->LogMsg(0, (char*)NULL, "Info, cfg->vm_config[%d].pw (%s) ", nCfgNum, cfg->vm_config[nCfgNum].pw);
		}

	}

	fclose(fp);
	return cfg;
}

