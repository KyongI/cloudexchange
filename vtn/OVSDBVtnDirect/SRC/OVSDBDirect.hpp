#ifndef _OVSDBDIRECT_HPP_
#define _OVSDBDIRECT_HPP_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <mysql.h>

#include "global.h"
#include "DbConnect.hpp"
#include "NeutronInfo.hpp"
#include "NovaInfo.hpp"
#include "PrintUtil.hpp"
#include "CWrap.hpp"

#define	BUFFER_SIZE		512
#define SEARCH_TYPE_ALL		0x01
#define SEARCH_TYPE_MDN		0x02
#define IPMD_TOTAL_LENGTH_LEN   4
#define LINE_MAX_LENGTH		8192


class COVSDBDirect
{
	public :
		COVSDBDirect();
		~COVSDBDirect();

		int				 Init	(CONFIG *a_stConf_);
		int				 Run	(int argc, char** argv);
		void			 Usage	(char *s);

		void			 ShowAllInfo		(void);
		void			 ShowTableInfo		(char *_tbname);
		void			 ShowKeyInfo		(char *_tbname);
		void			 ShowDBInfo			(char *_dbname);
		void			 ShowDBTableList	(char *_dbname);

	private :
		uint8_t			 m_unDbCnt;

		DbConnect		*m_pcDbConnect_[10];
		PrintUtil		*m_pcPrint;
		std::vector<KeystoneEndpoint>	stdEndp_;
		std::vector<KeystoneProject>	stdProj_;
		std::vector<KeystoneToken>		stdToken_;

		int				 m_nRet;
		char			 m_szHost[BUFFER_SIZE];
		char			 m_szUser[BUFFER_SIZE];
		char			 m_szPass[BUFFER_SIZE];
		char			 m_szDb[BUFFER_SIZE];
};

#endif
