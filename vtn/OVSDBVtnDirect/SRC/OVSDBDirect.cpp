#include "OVSDBDirect.hpp"

COVSDBDirect::COVSDBDirect()
{
	strcpy(m_szHost, "121.78.77.164");
	strcpy(m_szUser, "root");
	strcpy(m_szPass, "supersecret");
	strcpy(m_szDb, "neutron");
}

COVSDBDirect::~COVSDBDirect()
{
	if( m_pcDbConnect_ != NULL) {
		delete m_pcDbConnect_;
	}
}

int COVSDBDirect::Init()
{
	m_pcDbConnect_ = new DbConnect( &m_nRet, m_szHost, m_szUser, m_szPass, m_szDb);
	

	return ITF_OK;
}

void COVSDBDirect::Usage(char *s)
{
    printf("\n\n=====================================================================\n");
    printf("\n");
    printf("                      ODL OVSDB Viewer V1.0 \n");
    printf("\n");
    printf("=====================================================================\n");
    printf("\n");
    printf("USAGE:\n");
    printf("  %s [-aes] [file_name]\n", s);
    printf("\n");
    printf("DESCRIPTION:\n");
    printf("  This utility display OVSDB neutron information.\n");
    printf("  If there is no option key fields are output.\n");
    printf("\n");
    printf("OPTION:\n");
    printf("  a : All fields are output. \n");
    printf("  e : ERROR NUDs are output .\n");
    printf("  s {SearchID} {value} : search by ID, value. \n ");
    printf("  s + a : when used as a option to search in all fields. \n");
    printf("\n");
    printf("EXAMPLES:\n");
    printf("  %s -a OMP001_000_3CC_20130801_0000469.dat \n", s);
    printf("                                  Last Change : %s %s\n", __DATE__, __TIME__);
    printf("=====================================================================\n\n\n\n");
}

int COVSDBDirect::Run(int argc, char** argv)
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


	if (argc < 2) {
		Usage(argv[0]);
		exit(0);
	}

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
                Usage(argv[0]);
                exit(0);
        }
    }

    nFileCount = optind;
    if(nOptionS) nFileCount++ ;

    for ( ; nFileCount <= argc -1 ; nFileCount++)
    {
        strcpy(cFileName, argv[nFileCount]);

        if ((pFop = fopen(cFileName,"r")) < 0) {
            printf("[LOG] INPUT FILE OPEN ERROR");
            return -1;
        }

        cLineSave = (char*)malloc(LINE_MAX_LENGTH);

        while(fgets(cLineSave, LINE_MAX_LENGTH, pFop))
        {
            printf("%s \n",cLineSave);
        }

        fclose(pFop);
        free(cLineSave);

    } // for ( ; nFileCount <= argc -1 ; nFileCount++)

	return ITF_OK;
} 

int main(int argc, char *argv[])
{
	COVSDBDirect clsOVSDB;

	if( clsOVSDB.Init() == ITF_ERROR )
	{
		printf("Viewer Init() Error.\n");
		exit(ITF_EXIT_ABNORMAL);
	}

    if( clsOVSDB.Run(argc, argv) != ITF_OK ) exit(ITF_EXIT_ABNORMAL);
	else exit(ITF_EXIT_NORMAL);

	return ITF_OK;
}



