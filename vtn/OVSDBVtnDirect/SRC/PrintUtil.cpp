#include "PrintUtil.hpp"

PrintUtil::PrintUtil()
{
	m_pcNeutronInfo = NULL;
	m_pcNovaInfo = NULL;
	m_pcKeystoneInfo = NULL;
}

PrintUtil::~PrintUtil()
{
	if(m_pcNeutronInfo)
	{
		delete m_pcNeutronInfo;
	}

	if(m_pcNovaInfo)
	{
		delete m_pcNovaInfo;
	}

	if(m_pcKeystoneInfo)
	{
		delete m_pcKeystoneInfo;
	}
}

int PrintUtil::Initialize()
{
	if(m_pcNeutronInfo)
	{
		delete m_pcNeutronInfo;
	}

	if(m_pcNovaInfo)
	{
		delete m_pcNovaInfo;
	}

	if(m_pcKeystoneInfo)
	{
		delete m_pcKeystoneInfo;
	}

	m_pcNeutronInfo  = new CNeutronInfo();
	m_pcNovaInfo     = new CNovaInfo();
	m_pcKeystoneInfo = new CKeystoneInfo();

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
	
	return;
}

void PrintUtil::PrintNovaInfo(DbConnect *a_pclsDB)
{
	PrintCertificateInfo(a_pclsDB);
	PrintInstanceInfo(a_pclsDB);

	return;
}

void PrintUtil::PrintKeystoneInfo(DbConnect *a_pclsDB)
{
	PrintTokenInfo(a_pclsDB);
	PrintEndpointInfo(a_pclsDB);
	PrintProjectInfo(a_pclsDB);

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

void PrintUtil::PrintEndpointInfo(DbConnect *a_pclsDB, bool a_bMode) 
{
	stdEndp.clear();
	a_pclsDB->SelectDB((char*)"keystone");
	m_pcKeystoneInfo->Init(a_pclsDB);
	m_pcKeystoneInfo->GetEndpointInfo(stdEndp, (char*)"endpoint", a_bMode);

	return;
}

void PrintUtil::PrintProjectInfo(DbConnect *a_pclsDB, bool a_bMode)
{
	stdProj.clear();
	a_pclsDB->SelectDB((char*)"keystone");
	m_pcKeystoneInfo->Init(a_pclsDB);
	m_pcKeystoneInfo->GetProjectInfo(stdProj, (char*)"project", a_bMode);

	return;
}

void PrintUtil::PrintTokenInfo(DbConnect *a_pclsDB, bool a_bMode)
{
	stdToken.clear();
	a_pclsDB->SelectDB((char*)"keystone");
	m_pcKeystoneInfo->Init(a_pclsDB);
	m_pcKeystoneInfo->GetTokenInfo(stdToken, (char*)"token", a_bMode);

	return;
}
