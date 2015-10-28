#include "global.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <mysql.h>

#include "DbConnect.hpp"
#define MAX 1024

void usage(char *s)
{
    printf("\n\n=====================================================================\n");
    printf("\n");
    printf("                NUD Viewer V1.0 \n");
    printf("\n");
    printf("=====================================================================\n");
    printf("\n");
    printf("USAGE:\n");
    printf("  %s [-aes] [file_name]\n", s);
    printf("\n");
    printf("DESCRIPTION:\n");
    printf("  This utility display NUD format in file_named file\n");
    printf("  If there is no option key fields are output.\n");
    printf("  key fields : SYSTEM_NAME, REQUEST_TIME, RESPONSE_TIME, DELIVERY_RESULT, DELIVERY_STATUS, SYSTEM_DIVISION \n");
    printf("             : DCMF_PID,    BILL_FLAG,    NUD_TID,       CHARGE_AMOUNT,   CHARGE_PIVOT,    CHARGING_ID \n");
    printf("\n");
    printf("OPTION:\n");
    printf("  a : All fields are output. \n");
    printf("  e : ERROR NUDs are output .\n");
    printf("  s {SearchID} {value} : search by ID, value. \n ");
    printf("  s + a : when used as a option to search in all fields. \n");
    printf("\n");
    printf("EXAMPLES:\n");
    printf("  %s -a OMP001_000_3CC_20130801_0000469.dat \n", s);
    printf("  %s -e OMP001_000_3CC_20130801_0000469.dat \n", s);
    printf("  %s -s CHARGING_ID 01094085208 OMP001_000_3CC_20130801_0000469.dat \n", s);
    printf("  %s -s CHARGING_ID 01094085208 -a OMP001_000_3CC_20130801_0000469.dat \n", s);
    printf("                                  Last Change : %s %s\n", __DATE__, __TIME__);
    printf("=====================================================================\n\n\n\n");
}

int conf_loading()
{

    MYSQL     mysql;
    MYSQL_RES *res;
    MYSQL_ROW row;
    int       fields;

    mysql_init(&mysql);

    mysql_real_connect(&mysql,NULL, "jsk5225", "qlffld09","jsk5225",3306,"/opt/redmine-2.3.1-3/mysql/tmp/mysql.sock", 0);

    char szQueryResult[1024];
    sprintf(szQueryResult, "select * from nud_fromat");

     if(mysql_query(&mysql, szQueryResult) != NULL)
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

int run(int argc, char** argv)
{

    char cOption;
    int nOptionA = 0;
    int nOptionE = 0;
    int nOptionS = 0;

    char cFileName[80];
    FILE *pFop;
    char *cLineSave;
    int  nFileCount = 0;

    char* gSearchID;
    char* gSearchStr;

    int nPrintFlag = 0;


    while ((cOption = getopt(argc, argv, "aes:")) != -1 ){
        switch(cOption){
            case 'a':
                nOptionA = 1;
                nOptionE = 0;
                break;
            case 'e':
                nOptionE = 1;
                nOptionA = 0;
                nOptionS = 0;
                break;
            case 's':
                nOptionS = 1;
                nOptionE = 0;
                nPrintFlag = 0;
                gSearchID = optarg;
                gSearchStr = argv[optind];
                break;
            default :
                usage(argv[0]);
                exit(0);
        }
    }

    conf_loading();

    nFileCount = optind;
    if(nOptionS) nFileCount++ ;

    for ( ; nFileCount <= argc -1 ; nFileCount++)
    {
        strcpy(cFileName, argv[nFileCount]);

        if ((pFop = fopen(cFileName,"r")) < 0) {
            printf("[LOG] INPUT FILE OPEN ERROR");
            return -1;
        }

        cLineSave = (char*)malloc(MAX);

        while(fgets(cLineSave,MAX,pFop))
        {
            // printf("%s \n",cLineSave);
        }

        fclose(pFop);
        free(cLineSave);

    } // for ( ; nFileCount <= argc -1 ; nFileCount++)




} // int run(int argc, char** argv)

int main(int argc, char *argv[])
{

    if (argc < 2) {
        usage(argv[0]);
        exit(0);
    }

    run(argc, argv);

} // int main(int argc, char *argv[])



