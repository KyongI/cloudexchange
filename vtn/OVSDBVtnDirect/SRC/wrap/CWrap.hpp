#ifndef __WRAP_HPP_
#define __WRAP_HPP_

#include <stdio.h>

#include "CSingleLog.hpp"
#include "parser.h"

#define DEF_BUFFER_1024	1024
#define DEF_BUFFER_512	512
#define DEF_BUFFER_256	256


typedef struct _system_conf
{
	char system_id[10];
	char pcap_file_path[10];
	char server_ip[20];
	uint16_t	server_port;
	uint16_t	stat_change;
}SYSTEM_CONF;

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
