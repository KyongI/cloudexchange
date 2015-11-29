#include "DbConnect.hpp"

DbConnect::DbConnect(int *Ret, char *Host, char *User, char *Passwd, char *Name)
{
	result = NULL;
	isReconnect = false;
	DbTimeout = 0;
	ReadTimeout = 0;
	WriteTimeout = 0;

	SetDBString(Host, User, Passwd, Name) ;

	*Ret = 0;
}

DbConnect::~DbConnect()
{
	Disconnect();
}

//Set DB Information
int DbConnect::SetDBString(char *Host, char *User, char *Passwd, char *Name)
{
	memset(HostNamePri, 0x00, sizeof(HostNamePri));
	memset(UserName,    0x00, sizeof(UserName));
	memset(Password,    0x00, sizeof(Password));
	memset(Dbname,      0x00, sizeof(Dbname));

	if(Host)
	{
		memcpy(HostNamePri, Host, strlen(Host));
	}

	if(User)
	{
		memcpy(UserName, User, strlen(User));
	}

	if(Passwd)
	{
		memcpy(Password, Passwd, strlen(Passwd));
	}

	if(Name)
	{
		memcpy(Dbname, Name, strlen(Name));
	}

	return ITF_OK;
}

//DB Disconnect
int DbConnect::Disconnect()
{
	mysql_close(&mysql) ;

	printf(" DB disconnected\n");

	return ITF_OK;
}

int DbConnect::Ping()
{
	int	retry=0;

	if(!mysql_ping(&mysql))
	{
		return ITF_OK;
	}

	mysql_close(&mysql);
#if 0
	for (retry=0; retry<10; retry++)
	{
		if (RealConnect() == ITF_OK)
		{
			printf(" DB reconnected: tried %d times", retry+1);
			return ITF_OK;
		}
		sleep(6);
	}
#endif
	return ITF_ERROR;
}

//connect DB
int DbConnect::ConnectDB()
{
	isReconnect  = true;
	DbTimeout    = 10;
	ReadTimeout  = 10;
	WriteTimeout = 10;

	mysql_init(&mysql);
	mysql_options(&mysql, MYSQL_OPT_RECONNECT, &isReconnect);
	mysql_options(&mysql, MYSQL_OPT_CONNECT_TIMEOUT, (char*)&DbTimeout);
	mysql_options(&mysql, MYSQL_OPT_READ_TIMEOUT, (char*)&ReadTimeout);
	mysql_options(&mysql, MYSQL_OPT_WRITE_TIMEOUT, (char*)&WriteTimeout);

	if( mysql_real_connect(&mysql, 
							HostNamePri, 
							UserName, 
							Password, 
							Dbname, 
							3306, "/var/run/db.sock", 0) == NULL )
	{
		printf(" DB connect failed\n");
		return ITF_ERROR;
	}

	if(mysql_query(&mysql, (char*)"set names 'euckr'") != 0)
	{
		printf(" Query failed: set name 'euckr'\n");
		printf("  - Error No [%d]\n  - Error Msg [%s]\n", 
				mysql_errno(&mysql), mysql_error(&mysql));
		mysql_close(&mysql);
		return ITF_ERROR;
	}

	return ITF_OK;
}

//Execute SQL
int DbConnect::ExecuteSQL(char *query)
{
	if(Ping() != ITF_OK)
	{
		printf(" DB ping failure\n");
		return ITF_ERROR;
	}

	if(result)
	{
		mysql_free_result(result);
	}

	if(mysql_query(&mysql, query) != 0)
	{
		printf(" Query failed: %s\n", query);
		printf("  - Error No [%d] \n  - Error Msg [%s]\n", 
				mysql_errno(&mysql), mysql_error(&mysql));
		mysql_close(&mysql);
		return ITF_ERROR;
	}

	result = mysql_store_result(&mysql);

	if(result)
	{
		return result->row_count;
	}
	else
	{
		return 0;
	}
}
#if 0
int DbConnect::RealConnect()
{
	if( mysql_real_connect(&mysql, 
							HostNamePri, 
							UserName, 
							Password, 
							Dbname, 
							3306, "/var/run/db.sock", 0) == NULL )
	{
		printf(" DB connect failed\n");
		return ITF_ERROR;
	}

	return ITF_OK;
}
#endif
int DbConnect::SelectDB(char *_dbname)
{
	if(mysql_select_db(&mysql, _dbname) == ITF_ERROR)
	{
		mysql_close(&mysql);
		return ITF_ERROR;
	}
	printf(" DB [%s] is selected\n\n", _dbname);

	return ITF_OK;
}

MYSQL_RES* DbConnect::GetDBRes()
{
	return result;
}
