#include "DbConnect.hpp"

DbConnect::DbConnect(int *Ret, char *Host, char *User, char *Passwd, char *Name)
{
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

int DbConnect::Commit()
{
	return mysql_commit(&mysql) ;
}

int DbConnect::Rollback()
{
	return mysql_rollback(&mysql) ;
}

int DbConnect::Ping()
{
	int	retry=0;

	if(!mysql_ping(&mysql))
	{
		return ITF_OK;
	}

	mysql_close(&mysql);

	for (retry=0; retry<10; retry++)
	{
		if (RealConnect() == ITF_OK)
		{
			printf(" DB reconnected: tried %d times", retry+1);
			return ITF_OK;
		}
		sleep(6);
	}

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
				GetErrorNo(), GetError());
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
				GetErrorNo(), GetError());
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

const char *DbConnect::GetError()
{
	return mysql_error(&mysql);
}

int DbConnect::GetErrorNo()
{
	return mysql_errno(&mysql);
}

//Get Table data
int DbConnect::StoreResult(NUD_FORMAT *_nudformat)
{
	int		i = 0;

	if(!result)
	{
		printf("Result storing failed\n");
		return -1;
	}

	while((row = mysql_fetch_row(result)))
	{
		_nudformat[i].seq = atoi(row[0]);
		memcpy(_nudformat[i].format_name, row[1], strlen(row[1]));
		_nudformat[i].max_length = atoi(row[2]);
		memcpy(_nudformat[i].option_mo, row[3], strlen(row[3]));
		memcpy(_nudformat[i].data_type, row[4], strlen(row[4]));
		memcpy(_nudformat[i].default_value, row[5], strlen(row[5]));

		i++;
	}

	mysql_free_result(result);
	result = NULL;

	return 0;
}

int DbConnect::GetRow(NUD_FORMAT *_nudformat)
{
	if(!result)
	{
		printf("Failed to get rows\n");
		return -1;
	}

	row = mysql_fetch_row(result);

	if(row)
	{
		_nudformat->seq = atoi(row[0]);
		memcpy(_nudformat->format_name, row[1], strlen(row[1]));
		_nudformat->max_length = atoi(row[2]);
		memcpy(_nudformat->option_mo, row[3], strlen(row[3]));
		memcpy(_nudformat->data_type, row[4], strlen(row[4]));
		memcpy(_nudformat->default_value, row[5], strlen(row[5]));

		return 1;
	}
	else
	{
		mysql_free_result(result);
		result = NULL;

		return 0;
	}
}

