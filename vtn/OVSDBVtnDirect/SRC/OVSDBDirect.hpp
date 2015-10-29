#ifndef _OVSDBDIRECT_HPP_
#define _OVSDBDIRECT_HPP__

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <mysql.h>

#include "global.h"
#include "DbConnect.hpp"

#define	READ_BUFFER_SIZE     512
#define SEARCH_TYPE_ALL      0x01
#define SEARCH_TYPE_MDN      0x02
#define IPMD_TOTAL_LENGTH_LEN           4//addk

class COVSDBDirect 
{
	public :
		COVSDBDirect();
		~COVSDBDirect();

		int			Run( int argc, char** argv );
        int         Init();

	private :
		DbConnect*	m_pcDbConnect_;

		int			m_nRet;
		char*		m_szHost;
		char*		m_szUser;
		char*		m_szPass;
		char*		m_szDb;

		void		Usage(char *s);
}

#endif
