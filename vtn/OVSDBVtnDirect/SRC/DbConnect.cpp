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
    memset(HostNamePri,     0x00, sizeof(HostNamePri));
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

    return 0;

}

//DB Disconnect
int DbConnect::Disconnect()
{
    mysql_close(&mysql) ;

    printf("Disconnected DB\n");
    return 0;
}

//connect DB
int DbConnect::ConnectDB()
{
    mysql_init(&mysql);

    if( mysql_real_connect(&mysql, HostNamePri, UserName, Password, Dbname, 3306, "/var/run/db.sock", 0) == NULL )
    {
        printf("connect failed\n");
        return -1;
    }

    if(mysql_query(&mysql, (char*)"set names 'euckr'") != 0)
    {
        printf("Query failed\n");
                printf("Err Msg : %s\n", mysql_error(&mysql));
                mysql_close(&mysql);
                return -1;
        }

    printf("DbConnected\n");
    return 0;
}

//Execute SQL
int DbConnect::ExecuteSQL(char *query)
{
    if(result)
        mysql_free_result(result);

    if(mysql_query(&mysql, query) != 0)
    {
        printf("Query failed\n");
        printf("Err Msg : %s\n", mysql_error(&mysql));
        mysql_close(&mysql);
        return -1;
    }

    result = mysql_store_result(&mysql);

    if(result)
        return result->row_count;
    else
        return 0;
}

//Get Table data
int DbConnect::StoreResult(NUD_FORMAT *_nudformat)
{
    int i = 0;
    if(!result)
        printf("failed to Store Result\n");

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
		printf("failed to GetRows\n");

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

