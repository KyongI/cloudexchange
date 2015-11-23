#include "PrintUtil.hpp"

PrintUtil::PrintUtil()
{



}



PrintUtil::~PrintUtil()
{



}

int PrintUtil::Initialize()
{
	m_pcNeutronInfo = new CNeutronInfo();
	m_pcNovaInfo = new CNovaInfo();
	return 0;

}

void PrintUtil::PrintVM(int a_nVM)
{
	printf("###############################################################################\n");
	printf("#########                       VM [%2d]  DB Info                      #########\n", a_nVM);
	printf("###############################################################################\n");

	return;
}

void PrintUtil::PrintNeutronInfo(DbConnect *a_pclsDB)
{
	PrintNetworkInfo(a_pclsDB);		
	PrintSubnetInfo(a_pclsDB);		
	PrintPortInfo(a_pclsDB);		
	printf("\n\n");
	return ;
}

void PrintUtil::PrintNovaInfo(DbConnect *a_pclsDB)
{
	PrintCertificateInfo(a_pclsDB);
	PrintInstanceInfo(a_pclsDB);
	return;
}

void PrintUtil::PrintNetworkInfo(DbConnect *a_pclsDB)
{
	stdNetwork.clear();
	a_pclsDB->SelectDB((char*)"neutron");
	m_pcNeutronInfo->Init(a_pclsDB);	
	m_pcNeutronInfo->GetNetworksInfo(stdNetwork, (char*)"networks");
	return;
}

void PrintUtil::PrintSubnetInfo(DbConnect *a_pclsDB)
{
	stdSubnets.clear();
	a_pclsDB->SelectDB((char*)"neutron");
	m_pcNeutronInfo->Init(a_pclsDB);	
	m_pcNeutronInfo->GetSubnetsInfo(stdSubnets, (char*)"subnets");

	return;
}


void PrintUtil::PrintPortInfo(DbConnect *a_pclsDB)
{
	stdPorts.clear();
	a_pclsDB->SelectDB((char*)"neutron");
	m_pcNeutronInfo->Init(a_pclsDB);	
	m_pcNeutronInfo->GetPortsInfo(stdPorts, (char*)"ports");

	return;
}


void PrintUtil::PrintCertificateInfo(DbConnect *a_pclsDB)
{
	stdCerts.clear();
	a_pclsDB->SelectDB((char*)"nova");
	m_pcNovaInfo->Init(a_pclsDB);	
	m_pcNovaInfo->GetCertificatesInfo(stdCerts, (char*)"certificates");

	return;
}

void PrintUtil::PrintInstanceInfo(DbConnect *a_pclsDB)
{
	stdInst.clear();
	a_pclsDB->SelectDB((char*)"nova");
	m_pcNovaInfo->Init(a_pclsDB);	
	m_pcNovaInfo->GetInstancesInfo(stdInst, (char*)"instances");
	return;
}


