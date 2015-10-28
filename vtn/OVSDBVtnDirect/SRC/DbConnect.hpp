#ifndef _DB_CONNECTOR_
#define _DB_CONNECTOR_
#include "global.h"
#include <mysql.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

class DbConnect
{
    private :
        MYSQL   mysql;          //mysql Object
        MYSQL_RES   *result;    //mysql Result Set
        MYSQL_ROW   row ;       //mysql Row Set

        char HostNamePri[30];       //mysql Host name
        char UserName[30];      //mysql user name
        char Password[30];      //mysql user password
        char Dbname[30];        //mysql DB Name

    public:
        DbConnect(int *ret, char *Host, char *User, char *Passwd, char *Db);
        ~DbConnect();

        //Set DB Connect Information
        int SetDBString(char *Host, char *User, char *Passwd, char *Db);
        //Connect DB
        int ConnectDB();
        //Execute SQL Query
        int ExecuteSQL(char *query);
        //DB Disconnect
        int Disconnect();
        //Store member_info table data
        int StoreResult(NUD_FORMAT *_nudformat);
        //Get member_info Data by row
        int GetRow(NUD_FORMAT *_nudformat);

};

#endif
