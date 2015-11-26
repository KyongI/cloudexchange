#ifndef __WRAP_HPP_
#define __WRAP_HPP_

#include <stdio.h>

#include "CSingleLog.hpp"

#define DEF_BUFFER_1024	1024
#define DEF_BUFFER_512	512
#define DEF_BUFFER_256	256

#define DEF_MAX_CONFIG 10
typedef struct vm_config {
	char ip[40];
	char id[40];
	char pw[40];
} VM_CONF;

typedef struct config {
	VM_CONF	vm_config[DEF_MAX_CONFIG];
	uint8_t	unDbCnt;
} CONFIG;

class CWrap
{
	private:
		CSingleLog	*m_pLog;
		CONFIG		*m_pstConfig;
		char m_strProc[20];

	public:
		bool	bRun;

		CWrap(char *proc);
		~CWrap();

		int Initialize();
		CONFIG* InitConfig();	
		CSingleLog*	GetLog() { return m_pLog; }
		CONFIG*		GetConfig() { return m_pstConfig; }




};


#endif
