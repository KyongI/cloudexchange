#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "DbConnect.hpp"
#include "NeutronInfo.hpp"
#include "NovaInfo.hpp"
#include "KeystoneInfo.hpp"

class PrintUtil
{
	private:
		CNeutronInfo	*m_pcNeutronInfo;
		CNovaInfo		*m_pcNovaInfo;
		CKeystoneInfo	*m_pcKeystoneInfo;

		std::vector<NeutronNetworks>    stdNetwork;
		std::vector<NeutronSubnets>     stdSubnets;
		std::vector<NeutronPorts>       stdPorts;
		std::vector<NovaCerti>          stdCerts;
		std::vector<NovaInstances>      stdInst;
		std::vector<KeystoneEndpoint>   stdEndp;
		std::vector<KeystoneProject>    stdProj;
		std::vector<KeystoneToken>      stdToken;

	public:
		PrintUtil();
		~PrintUtil();

		int		Initialize				();
		
		void	PrintVM					(int a_nVM);
		void	PrintNeutronInfo		(DbConnect *a_pclsDB);
		void	PrintNovaInfo			(DbConnect *a_pclsDB);
		void	PrintKeystoneInfo		(DbConnect *a_pclsDB);
		void	PrintNetworkInfo		(DbConnect *a_pclsDB);
		void	PrintSubnetInfo			(DbConnect *a_pclsDB);
		void	PrintPortInfo			(DbConnect *a_pclsDB);
		void	PrintCertificateInfo	(DbConnect *a_pclsDB);
		void	PrintInstanceInfo		(DbConnect *a_pclsDB);
		void	PrintEndpointInfo		(DbConnect *a_pclsDB, bool a_bMode = true);
		void	PrintProjectInfo		(DbConnect *a_pclsDB, bool a_bMode = true);
		void	PrintTokenInfo			(DbConnect *a_pclsDB, bool a_bMode = true);
		void	PrintNeutronTablelist	(DbConnect *a_pclsDB);
		void	PrintNovaTablelist		(DbConnect *a_pclsDB);
		void	PrintKeystoneTablelist	(DbConnect *a_pclsDB);
};
