#include "NeutronTest.hpp"

CNeutronTest::CNeutronTest()
{
	m_pcDbConnect_ = NULL;
}

CNeutronTest::~CNeutronTest()
{

}

int CNeutronTest::Init(DbConnect* pcDbConnect) 
{
	m_pcDbConnect_ = pcDbConnect;
	return ITF_OK;
}

int CNeutronTest::TestNetwork()
{
	printf("--- neutron::networks --------------------------------------------------\n");
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

	return ITF_OK; 
}

