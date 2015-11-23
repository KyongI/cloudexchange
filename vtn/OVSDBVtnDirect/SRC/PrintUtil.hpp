#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "DbConnect.hpp"
#include "NeutronInfo.hpp"
#include "NovaInfo.hpp"

class PrintUtil
{
	private:
		CNeutronInfo	*m_pcNeutronInfo;
		CNovaInfo		*m_pcNovaInfo;

		std::vector<NeutronNetworks>    stdNetwork;
		std::vector<NeutronSubnets>     stdSubnets;
		std::vector<NeutronPorts>       stdPorts;
		std::vector<NovaCerti>          stdCerts;
		std::vector<NovaInstances>      stdInst;


	public:
		PrintUtil();
		~PrintUtil();
		int Initialize();
		void PrintVM(int a_nVM);
		void PrintNeutronInfo(DbConnect *a_pclsDB);
		void PrintNovaInfo(DbConnect *a_pclsDB);
		void PrintNetworkInfo(DbConnect *a_pclsDB);
		void PrintSubnetInfo(DbConnect *a_pclsDB);
		void PrintPortInfo(DbConnect *a_pclsDB);
		void PrintCertificateInfo(DbConnect *a_pclsDB);
		void PrintInstanceInfo(DbConnect *a_pclsDB);

};
