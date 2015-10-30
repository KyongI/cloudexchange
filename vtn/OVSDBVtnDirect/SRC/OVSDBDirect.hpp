#ifndef _OVSDBDIRECT_HPP_
#define _OVSDBDIRECT_HPP__

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <mysql.h>

#include "global.h"
#include "DbConnect.hpp"

#define	BUFFER_SIZE		512
#define SEARCH_TYPE_ALL			0x01
#define SEARCH_TYPE_MDN			0x02
#define IPMD_TOTAL_LENGTH_LEN   4
#define LINE_MAX_LENGTH			8192

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
		char		m_szHost[BUFFER_SIZE];
		char		m_szUser[BUFFER_SIZE];
		char		m_szPass[BUFFER_SIZE];
		char		m_szDb[BUFFER_SIZE];

		void		Usage(char *s);
};

#endif
