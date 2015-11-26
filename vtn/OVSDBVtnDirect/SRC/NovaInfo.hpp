#ifndef _NOVAINFO_HPP_
#define _NOVAINFO_HPP_
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <mysql.h>
#include <vector>

#include "global.h"
#include "DbConnect.hpp"
#include "OVSDBDefine.hpp"

class CNovaInfo
{
	public:
		 CNovaInfo();
		~CNovaInfo();

		int			 Init(DbConnect* pcDbConnect);

		int			 GetCertificatesInfo(std::vector<NovaCerti> &_vecCert, 
										 char *_tbName,
										 bool _vmode=true);
		int			 GetInstancesInfo(std::vector<NovaInstances> &_vecInst, 
									  char *_tbName,
									  bool _vmode=true);
		int			 ShowTableInfo(void);

	private:
		DbConnect	*m_pcDbConnect_;
		MYSQL_RES	*m_pResult;
		MYSQL_ROW	 row;

};

#endif
