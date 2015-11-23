#ifndef _DB_QUERY_HPP
#define _DB_QUERY_HPP	1

#include <unistd.h>
#include <stdio.h>
#include <mysql.h>
#include <iostream>
#include <vector>
#include <map>

#include <stdint.h>
#include "CSingleLog.hpp"

#define BUFF_LEN	32

#define	MAX_DB_TRY_COUNT			5		// Temporary
#define	DB_RECONNECT_SLEEP_PERIOD	2
#define	DB_RECONNECT_USLEEP_PERIOD	100000
#define DB_CONNECT_TIMEOUT			3		// 3 sec
#define DB_READ_TIMEOUT				5		// 5 sec (real_time = 15 sec)
#define DB_WRITE_TIMEOUT			5		// 5 sec (real_time = 15 sec)

#define MAX_SECONDARY_DB_TRY_COUNT	1

#define PRIMARY_DB		1
#define SECONDARY_DB	2

#define	DB_STR_REMOTE				"REMOTE"
#define	DB_STR_LOCAL				"LOCAL "


//Define Error Code
#define DB_CONNECT_ERROR	-101
#define DB_SELECT_ERROR		-102
#define DB_EXEC_SQL_ERROR	-103

using namespace std;

typedef map<uint16_t, string>	tuple_t ;	// Tuple
typedef vector<tuple_t>		tuples_t ;	// Tuples

class DbQuery
{
	private:
		MYSQL		mysql ;				// Mysql
		MYSQL_RES	*result ;			// ResultSet
		MYSQL_ROW	row ;				// Record

		char HostNamePri[BUFF_LEN] ;	// DB HostName Primary
		char HostNameSec[BUFF_LEN] ;	// DB HostName Secondary
		char UserName[BUFF_LEN] ;		// DB UserName
		char Password[BUFF_LEN] ;		// DB Password
		char DbName[BUFF_LEN] ;			// DB Name

		char*	m_pDBWhere;
		
		CSingleLog*	pLOG;
	
		MYSQL	mysql2 ;				// Mysql
		char*	pDB2;
		
	public:
		DbQuery(int *Ret, char *, char *, char *, char *, CSingleLog *) ;
		~DbQuery() ;

		char*	pDBPri;
		char*	pDBSec;
		char*	pDBUser;
		char*	pDBPasswd;
		char*	pDBName;

		// Set DB Misc..
		void SetDbMisc(char *, char *, char *, char *) ;
	
		// Connect to Database
		int EnableDb() ;
		int EnableDb_Secondary();
		
		// Disconnect to Database
		void DisableDb() ;

		// Execute SQL Query (insert, update, ...)
		int ExecuteSQL(char *) ;
		int ExecuteSQL_Secondary(char *);
		
		// Open SQL Query (select)
		int OpenSQL(char *, tuples_t *) ;

		// Close ResultSet
		void CloseResultSet(tuples_t *) ;

		// Ping to Database
		int PingToDb() ;
		
		// mysql_insert_id()
		my_ulonglong insert_id()		{ return mysql_insert_id(&mysql); }
		// mysql_affected_rows()
		int Affected_Rows()				{ return mysql_affected_rows(&mysql); }
		
} ;

#endif

