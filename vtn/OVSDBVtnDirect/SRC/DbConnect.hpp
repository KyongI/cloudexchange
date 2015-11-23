#ifndef _DB_CONNECTOR_
#define _DB_CONNECTOR_
#include "global.h"
#include <mysql.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

class DbConnect
{
	private :
		MYSQL		 mysql;			//mysql Object
		MYSQL_RES	*result;		//mysql Result Set
		MYSQL_ROW	 row ;			//mysql Row Set

		char		 HostNamePri[30];	//mysql Host name
		char		 UserName[30];		//mysql user name
		char		 Password[30];		//mysql user password
		char		 Dbname[30];		//mysql DB Name

		bool			isReconnect;
		unsigned int	DbTimeout;
		unsigned int	ReadTimeout;
		unsigned int	WriteTimeout;

	public:
		DbConnect(int *ret, char *Host, char *User, char *Passwd, char *Db);
		~DbConnect();

		int			 SetDBString(char *Host, char *User, char *Passwd, char *Db);
		int			 ConnectDB();
		int			 ExecuteSQL(char *query);
		int			 RealConnect();
		int			 Disconnect();
		int			 Commit();
		int			 Rollback();
		int			 Ping();
		int			 SelectDB(char *_dbname);

		int			 StoreResult(NUD_FORMAT *_nudformat);
		int			 GetRow(NUD_FORMAT *_nudformat);

		MYSQL_RES	*GetDBRes();
		const char	*GetError();
		int			 GetErrorNo();

};

#endif
