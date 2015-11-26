#ifndef _NEUTRONINFO_HPP_
#define _NEUTRONINFO_HPP_
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <mysql.h>
#include <vector>

#include "global.h"
#include "DbConnect.hpp"
#include "OVSDBDefine.hpp"

class CNeutronInfo
{
	public:
		 CNeutronInfo();
		~CNeutronInfo();

		int			 Init(DbConnect* pcDbConnect);

		int			 GetNetworksInfo(std::vector<NeutronNetworks> &_vecNet, 
									 char *_tbName,
									 bool _vmode=true);
		int			 GetSubnetsInfo(std::vector<NeutronSubnets> &_vecSubn, 
									char *_tbName,
									bool _vmode=true);
		int			 GetPortsInfo(std::vector<NeutronPorts> &_vecPort, 
								  char *_tbName,
								  bool _vmode=true);
		int			 ShowTableInfo(void);

	private:
		DbConnect	*m_pcDbConnect_;
		MYSQL_RES	*m_pResult;
		MYSQL_ROW	 row;

};

#endif
