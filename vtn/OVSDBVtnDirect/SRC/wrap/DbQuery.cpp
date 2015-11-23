/*---------------------------------------------------------------------------
| Project		: PA&C (Packet Analysis & Control)
| Filename		: DbQuery.cpp
| Description	: Transact Database Query
| Date			: 2007. 05. 14
| Made by		: Keywon Ryu <ryujeen@ntels.com>
|--------------------------------------------------------------------------*/

#include "DbQuery.hpp"

DbQuery::DbQuery(int *Ret, 
	char *Host, char *User, char *Passwd, char *Name, CSingleLog *pLog)
{
	pLOG		= pLog;
	/* 1) Set Database Misc... */	
	SetDbMisc(Host, User, Passwd, Name) ;

	pDBPri 		= HostNamePri;
	pDBSec 		= HostNameSec;
	pDBUser		= UserName;
	pDBPasswd	= Password;
	pDBName		= DbName;

	/* 2) Connect to Database */
	*Ret = EnableDb() ;

	result = NULL ;

	pDB2	= NULL ;
}

DbQuery::~DbQuery()
{
	/* 1) Disconnect to Database */
	DisableDb() ;
}

/*-------------------------------------------------------------------------
| Name : SetDbMisc
| Func : Set Database Misc...
| Args : char * (Database HostNamePri)
|      : char * (Database UserName)
|      : char * (Database Password)
|      : char * (Database Name)
| Rets : void
|------------------------------------------------------------------------*/
void DbQuery::SetDbMisc(char *Host, char *User, char *Passwd, char *Name)
{
	int		nRet;

	/* 1) Set Variables to Zero Memory */
	memset(HostNamePri, 0x00, sizeof ( HostNamePri )) ;
	memset(HostNameSec, 0x00, sizeof ( HostNameSec )) ;

	memset(UserName, 0x00, sizeof(UserName)) ;
	memset(Password, 0x00, sizeof(Password)) ;
	memset(DbName, 0x00, sizeof(DbName)) ;

	/* 2) Set HostNamePri, UserName, Password, DbName */
	if ( Host )
	{
		memcpy(HostNamePri, Host, strlen(Host)) ;
		memcpy(HostNameSec, Host, strlen(Host)) ;
	}
	if ( User )
		memcpy(UserName, User, strlen(User)) ;
	if ( Passwd )
		memcpy(Password, Passwd, strlen(Passwd)) ;
	if ( Name )
		memcpy(DbName, Name, strlen(Name)) ;
}

/*--------------------------------------------------------------------------
| Name : EnableDb
| Func : Connect to Database. Ready to Use Database
| Args : void
| Rets : int 0(Success), Error Value(Fail)
|-------------------------------------------------------------------------*/
int DbQuery::EnableDb()
{
	static 	int 	nTryCount;
	static	char*	pHOST;
	unsigned int	nDBTimeout 		= DB_CONNECT_TIMEOUT ;
	unsigned int	nREADTimeout	= DB_READ_TIMEOUT ; 
	unsigned int	nWRITETimeout	= DB_WRITE_TIMEOUT ;
	
	/* 1) Initialize Mysql */
	/*
	mysql_init(&mysql) ;
	mysql_options(&mysql, MYSQL_OPT_CONNECT_TIMEOUT, (char*)&nDBTimeout) ; 
	mysql_options(&mysql, MYSQL_OPT_READ_TIMEOUT, (char*)&nREADTimeout) ;
	mysql_options(&mysql, MYSQL_OPT_WRITE_TIMEOUT, (char*)&nWRITETimeout) ;
	*/
	/* 2) Connect to Mysql Database */
	for ( nTryCount = 0; nTryCount < MAX_DB_TRY_COUNT; nTryCount++ ){
		mysql_init(&mysql) ;
		mysql_options(&mysql, MYSQL_OPT_CONNECT_TIMEOUT, (char*)&nDBTimeout) ; 
		mysql_options(&mysql, MYSQL_OPT_READ_TIMEOUT, (char*)&nREADTimeout) ;
		mysql_options(&mysql, MYSQL_OPT_WRITE_TIMEOUT, (char*)&nWRITETimeout) ;

		if ( mysql_real_connect(&mysql, pDBPri, UserName, Password, DbName, 0, NULL, 0))
			break;

		if ( pLOG != NULL )
			pLOG->LogMsg( 0, (char*)NULL, "NOTI, DB_TRY_CNT[%d]", nTryCount) ;
		usleep ( DB_RECONNECT_USLEEP_PERIOD );
	}
	
	if ( nTryCount == MAX_DB_TRY_COUNT )
		return DB_CONNECT_ERROR ;

	/* 3) Set Database for Using */
	if ( mysql_select_db(&mysql, pDBPri ) == -1 )
	{
		mysql_close(&mysql) ;
		return DB_SELECT_ERROR ;
	}

	if ( pLOG != NULL )
		pLOG->LogMsg ( 0, (char*)NULL, "NOTI, DB:Connected DB host[%s]", pDBPri );

	return 0 ;
}

int DbQuery::EnableDb_Secondary()
{
	static 	int 	nTryCount;
	static	char*	pHOST;
	unsigned int	nDBTimeout 		= DB_CONNECT_TIMEOUT ;
	unsigned int	nREADTimeout	= DB_READ_TIMEOUT ; 
	unsigned int	nWRITETimeout	= DB_WRITE_TIMEOUT ;
	
	if (pDB2) {
		mysql_close(&mysql2);
		pDB2 = NULL;
	}
	
	/* 1) Initialize Mysql */
	/*
	mysql_init(&mysql2) ;
	mysql_options(&mysql2, MYSQL_OPT_CONNECT_TIMEOUT, (char*)&nDBTimeout) ; 
	mysql_options(&mysql2, MYSQL_OPT_READ_TIMEOUT, (char*)&nREADTimeout) ;
	mysql_options(&mysql2, MYSQL_OPT_WRITE_TIMEOUT, (char*)&nWRITETimeout) ;
	*/
	/* 2) Connect to Mysql Database */
	
	for ( nTryCount = 0; nTryCount < MAX_SECONDARY_DB_TRY_COUNT; nTryCount++ ){
		mysql_init(&mysql2) ;
		mysql_options(&mysql2, MYSQL_OPT_CONNECT_TIMEOUT, (char*)&nDBTimeout) ; 
		mysql_options(&mysql2, MYSQL_OPT_READ_TIMEOUT, (char*)&nREADTimeout) ;
		mysql_options(&mysql2, MYSQL_OPT_WRITE_TIMEOUT, (char*)&nWRITETimeout) ;
		
		if ( mysql_real_connect(&mysql2, pDBSec, UserName, Password, DbName, 0, NULL, 0))
			break;
	
		if ( pLOG != NULL )
			pLOG->LogMsg( 0, (char*)NULL, "NOTI, DB_TRY_CNT[%d]", nTryCount) ;
		usleep ( DB_RECONNECT_USLEEP_PERIOD );
	}
	
	if ( nTryCount == MAX_SECONDARY_DB_TRY_COUNT )
		return DB_CONNECT_ERROR ;

	/* 3) Set Database for Using */
	if ( mysql_select_db(&mysql2, DbName ) == -1 )
	{
		mysql_close(&mysql2) ;
		return DB_SELECT_ERROR ;
	}

	if ( pLOG != NULL )
		pLOG->LogMsg ( 0, (char*)NULL, "NOTI, DB:Connected DB host[%s][%s]", m_pDBWhere, pDB2 );
	
	pDB2 = pDBSec;
	return 0 ;
}

/*--------------------------------------------------------------------------
| Name : DisableDb
| Func : Disconnect to Database
| Args : void
| Rets : void
|-------------------------------------------------------------------------*/
void DbQuery::DisableDb()
{
	/* 1) Disconnect to Database */
	mysql_close(&mysql) ;
	
	if (pDB2) {
		mysql_close(&mysql2);
		pDB2 = NULL;
	}
}

/*--------------------------------------------------------------------------
| Name : ExecuteSQL
| Func : Execute SQL Query (INSERT, UPDATE, DELETE, ...)
| Args : char * (Query)
| Rets : int 0(Success), Error Value(Fail)
|-------------------------------------------------------------------------*/
int DbQuery::ExecuteSQL(char *Query)
{
	/* 1) Execute SQL Query */
	if ( mysql_ping(&mysql) != 0 )
		goto LOST_CONNECT ;

	if ( mysql_query(&mysql, Query) != 0 )
	{
		if ( pLOG )
		{
			pLOG->LogMsg(0, (char*)NULL, "FALT, DB_ERROR[%d]:[%s] Query = %s", 
				mysql_errno(&mysql), mysql_error(&mysql), Query) ;
		}

LOST_CONNECT:
		if ( pLOG )
			pLOG->LogMsg(0, (char*)NULL, "FALT, LOST_CONNECTION DB_ERROR[%d]:[%s]",
				mysql_errno(&mysql), mysql_error(&mysql)) ;
		mysql_close(&mysql) ;

		if ( !EnableDb() )
		{
			if ( mysql_query(&mysql, Query) != 0 )
			{
				if ( pLOG )
				{
					pLOG->LogMsg(0, (char*)NULL, "FALT, DB_ERROR(2)[%d]:[%s] Query = %s", 
						mysql_errno(&mysql), mysql_error(&mysql), Query) ;
				}
				mysql_close(&mysql) ;
				return DB_EXEC_SQL_ERROR ;
			}
		}
		else
			return DB_EXEC_SQL_ERROR ;
	}

	return 0 ;
}

int DbQuery::ExecuteSQL_Secondary(char *Query)
{
	if (pDB2 != pDBSec) {
#ifdef  _WIUX_ONE_BOX_
#else
                mysql_close(&mysql2);
#endif

		pDB2 = NULL;
	}
	if (pDB2 == NULL) {
		EnableDb_Secondary();
		if (pDB2 == NULL) return DB_EXEC_SQL_ERROR;
	}
		
	
	/* 1) Execute SQL Query */
	if ( mysql_ping(&mysql2) != 0 )
		return DB_EXEC_SQL_ERROR;

	if ( mysql_query(&mysql2, Query) != 0 )
	{
		if ( pLOG )
		{
			pLOG->LogMsg(0, (char*)NULL, "FALT, DB_ERROR[%d]:[%s] Query = %s", 
				mysql_errno(&mysql), mysql_error(&mysql), Query) ;
		}

		mysql_close(&mysql2) ;
		pDB2 = NULL;

	}

	return 0 ;
}
	
/*---------------------------------------------------------------------------
| Name : OpenSQL
| Func : Open SQL Query (SELECT)
| Args : char * (Query)
|      : tuples_t * (Result Tuples)
| Rets : int (Tuples)
|--------------------------------------------------------------------------*/
int DbQuery::OpenSQL(char *Query, tuples_t *Tuples)
{
	CloseResultSet(Tuples) ;

	/* 1) Execute SQL Query */
	if ( mysql_ping(&mysql) != 0 )
		goto LOST_CONNECT ;

	if ( mysql_query(&mysql, Query) != 0 )
	{
		if ( pLOG )
		{
			pLOG->LogMsg(0, (char*)NULL, "FALT, DB_ERROR[%d]:[%s] Query = %s", 
				mysql_errno(&mysql), mysql_error(&mysql), Query) ;
		}
	
LOST_CONNECT:
		if ( pLOG )
			pLOG->LogMsg(0, (char*)NULL, "FALT, LOST_CONNECTION DB_ERROR[%d]:[%s]",
				mysql_errno(&mysql), mysql_error(&mysql)) ;
		mysql_close(&mysql) ;

		if ( !EnableDb() )
		{
			if ( mysql_query(&mysql, Query) != 0 )
			{
				if ( pLOG )
				{
					pLOG->LogMsg(0, (char*)NULL, "FALT, DB_ERROR(2)[%d]:[%s] Query = %s", 
						mysql_errno(&mysql), mysql_error(&mysql), Query) ;
				}
				mysql_close(&mysql) ;
				return DB_EXEC_SQL_ERROR ;
			}
		}
		else
			return DB_EXEC_SQL_ERROR ;
	}

	/* 2) Get Result Tuples from Database */
	tuple_t Tuple ;
	result = mysql_use_result(&mysql) ;
	while ( row = mysql_fetch_row(result) )
	{
		Tuple.clear();

		/* 3) Set Tuples from Result */
		for ( int i = 0 ; i < result->field_count ; i++ )
		{
			/* 4) Set Tuple about Row */
			if ( row[i] && strlen(row[i]))
//				Tuple.insert(pair<string, string>(result->fields[i].name, row[i])) ;
				Tuple.insert(pair<uint16_t, string>(i, row[i])) ;
			else
//				Tuple.insert(pair<string, string>(result->fields[i].name, "")) ;
				Tuple.insert(pair<uint16_t, string>(i, " ")) ;
		}
		/* 5) Add Tuple to Vector */
		Tuples->push_back(Tuple) ;
	}

	/* 6) Free Result Tuples */
	mysql_free_result(result) ;
	result = NULL ;

	return Tuples->size();
}

/*---------------------------------------------------------------------------
| Name : CloseResultSet
| Func : Close ResultSet
| Args : tuples_t * (Result Tuples)
| Rets : void
|--------------------------------------------------------------------------*/
void DbQuery::CloseResultSet(tuples_t *Tuples)
{
	/* 1) Clear Result Tuples */
	Tuples->clear() ;
}

/*---------------------------------------------------------------------------
| Name : PingToDb
| Func : Ping to Database
| Args : void
| Rets : int (mysql_ping return value)
|--------------------------------------------------------------------------*/
int DbQuery::PingToDb()
{
	/* 1) Return mysql_ping */
	return mysql_ping(&mysql) ;
}

