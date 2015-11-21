#include "OVSDBDirect.hpp"

COVSDBDirect::COVSDBDirect()
{
	strcpy(m_szHost, "121.78.77.163");
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
	m_pcDbConnect_->ConnectDB();

	m_pcNeutronTest_ = new CNeutronTest();

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
	printf("  %s [-d]\n", s);
	printf("\n");
	printf("DESCRIPTION:\n");
	printf("  This utility display OVSDB neutron information.\n");
	printf("  If there is no option key fields are output.\n");
	printf("\n");
	printf("OPTION:\n");
	printf("  d : debug print output. \n");
	printf("\n");
	printf("EXAMPLES:\n");
	printf("                                  Last Change : %s %s\n", __DATE__, __TIME__);
	printf("=====================================================================\n\n\n\n");
}

int COVSDBDirect::Run(int argc, char** argv)
{

	char cOption;
	int  nOptionA = 0;
	char cFileName[80];
	FILE *pFop;
	char *cLineSave;
	int  nFileCount = 0;
	char *gSearchID;
	char *gSearchStr;
	int  nPrintFlag = 0;

	while ((cOption = getopt(argc, argv, "des:")) != -1 ){
		switch(cOption){
			case 'd':
				nOptionA = 1;
				break;
			case 'e':
				nOptionA = 0;
				break;
			case 's':
				nPrintFlag = 0;
				gSearchID = optarg;
				gSearchStr = argv[optind];
				break;
			default :
				Usage(argv[0]);
				exit(0);
		}
	}

	m_pcNeutronTest_->Init(m_pcDbConnect_);
	m_pcNeutronTest_->TestNetwork();
	
	printf("--- neutron::networks --------------------------------------------------\n");
	int nRowCount = m_pcDbConnect_->ExecuteSQL((char*)"select * from networks");
	MYSQL_RES *result = m_pcDbConnect_->GetDBRes();
	MYSQL_ROW row;
	int fields = mysql_num_fields(result);

	while((row = mysql_fetch_row(result)))
	{
		for(int cnt = 0 ; cnt < fields ; ++cnt)
			printf(" %s ||", row[cnt]);
		printf("\n");
	}
	printf("\n");
	
	printf("--- neutron::subnets --------------------------------------------------\n");
	nRowCount = m_pcDbConnect_->ExecuteSQL((char*)"select * from subnets");
	result = m_pcDbConnect_->GetDBRes();
	fields = mysql_num_fields(result);

	while((row = mysql_fetch_row(result)))
	{
		for(int cnt = 0 ; cnt < fields ; ++cnt)
			printf(" %s ||", row[cnt]);
		printf("\n");
	}
	printf("\n");

	printf("--- neutron::routers --------------------------------------------------\n");
	nRowCount = m_pcDbConnect_->ExecuteSQL((char*)"select * from routers");
	result = m_pcDbConnect_->GetDBRes();
	fields = mysql_num_fields(result);

	while((row = mysql_fetch_row(result)))
	{
		for(int cnt = 0 ; cnt < fields ; ++cnt)
			printf(" %s ||", row[cnt]);
		printf("\n");
	}
	printf("\n");

	printf("--- neutron::ports --------------------------------------------------\n");
	nRowCount = m_pcDbConnect_->ExecuteSQL((char*)"select * from ports");
	result = m_pcDbConnect_->GetDBRes();
	fields = mysql_num_fields(result);

	while((row = mysql_fetch_row(result)))
	{
		for(int cnt = 0 ; cnt < fields ; ++cnt)
			printf(" %s ||", row[cnt]);
		printf("\n");
	}
	printf("\n");

	printf("--- neutron::ip allocations --------------------------------------------------\n");
	nRowCount = m_pcDbConnect_->ExecuteSQL((char*)"select * from ipallocations");
	result = m_pcDbConnect_->GetDBRes();
	fields = mysql_num_fields(result);

	while((row = mysql_fetch_row(result)))
	{
		for(int cnt = 0 ; cnt < fields ; ++cnt)
			printf(" %s ||", row[cnt]);
		printf("\n");
	}
	printf("\n");



	nFileCount = optind;

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



