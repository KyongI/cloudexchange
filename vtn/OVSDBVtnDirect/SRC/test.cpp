#include<stdio.h>
#include<stdlib.h>
#include<errno.h>
#include<mysql.h>

int main()
{
        MYSQL     mysql;
        MYSQL_RES *res;
        MYSQL_ROW row;
        int       fields;

        mysql_init(&mysql);

        mysql_real_connect(&mysql, "121.78.77.164", "root", "supersecret", "neutron", 3306, "/var/run/db.sock", 0);

        char szQueryResult[1024];
        sprintf(szQueryResult, "show tables");

         if(mysql_query(&mysql, szQueryResult) != 0)
         {
                 printf("%s\n", mysql_error(&mysql));
                 exit(1);
         }

         res = mysql_store_result( &mysql ) ;
         fields = mysql_num_fields(res) ;

         while((row = mysql_fetch_row(res)))
         {
                  //for(int cnt = 0 ; cnt < fields ; ++cnt)
                          printf(" %s ||", row[0]);

                  //printf("\n");
         }
         printf("\n");

         mysql_free_result(res);
         mysql_close(&mysql);
}
           
