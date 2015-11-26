#ifndef _KEYSTONEINFO_HPP_
#define _KEYSTONEINFO_HPP_
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <mysql.h>
#include <vector>

#include "global.h"
#include "DbConnect.hpp"
#include "OVSDBDefine.hpp"

#define KEYSTONE_ID_LEN			32
#define UUID_LEN				36
#define	UUID_TIME_LOW			8
#define UUID_TIME_MID			4
#define UUID_TIME_HIGH_VERSION	4
#define UUID_CLOCK_SEQ			4
#define UUID_TIME_NODE			12
#define UUID_VERSION_POS		12

class CKeystoneInfo
{
	public:
		 CKeystoneInfo();
		~CKeystoneInfo();

		uint32_t	 Init					(DbConnect* pcDbConnect);

		char		*ConvertIDToUUID		(char *a_strID);
		char		*ConvertUUIDToVTNKey	(char *a_uuid);

		uint32_t	 GetEndpointInfo		(std::vector<KeystoneEndpoint> &_vecEndp, 
											 char *_tbName,
											 bool _vmode=true);
		uint32_t	 GetProjectInfo			(std::vector<KeystoneProject> &_vecProj, 
											 char *_tbName,
											 bool _vmode=true);
		uint32_t	 GetTokenInfo			(std::vector<KeystoneToken> &_vecToken, 
											 char *_tbName,
											 bool _vmode=true);
		uint32_t	 ShowTableInfo			(void);

	private:
		DbConnect	*m_pcDbConnect_;
		MYSQL_RES	*m_pResult;
		MYSQL_ROW	 row;

};

#endif
