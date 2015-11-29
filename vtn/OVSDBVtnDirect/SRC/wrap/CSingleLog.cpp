#include "CSingleLog.hpp"

CSingleLog*	CSingleLog::the_config = 0;

CSingleLog::CSingleLog()
{
	memset(&m_LOG, 0, sizeof(log_templete));
	memset(__log_base__, 0x00, sizeof(__log_base__));
	g_nLocalDiff = 0;
	m_nLevel = 0;
	memset(g_szTimeStr, 0x00, sizeof(g_szTimeStr));
	m_lID = 0;
}

bool CSingleLog::Initialize( char* pPROC, unsigned long long uID, char* pBASE )
{
	m_nLevel	= 3;

	CalcDiffEpochFromLocal() ;
	StartFile ( pBASE, pPROC, uID );

	return true;
}

// Epoch 시간 계산
void CSingleLog::CalcDiffEpochFromLocal()
{
	struct tm	tTime ;
	
	tTime.tm_year	= 1970 - 1900 ;
	tTime.tm_mon	= 1 - 1 ;
	tTime.tm_mday	= 1 ;
	tTime.tm_hour	= 0 ;
	tTime.tm_min	= 0 ;
	tTime.tm_sec	= 0 ;

	g_nLocalDiff = (int)mktime(&tTime) ;
}

void CSingleLog::StartFile ( char* pBASE, char* pPROC, unsigned long long uID )
{
	m_lID	= uID;
	
	InitLog ( &m_LOG );

	SetLogBase ( pBASE );
	SetLogDev ( LOG_DEV_FILE_APPEND | LOG_DEV_WITHDATE );
	SetLogFile ((const char*)pPROC );
	SetLogLevel ( m_nLevel );
}

void CSingleLog::AdjustFileName( time_t tNow)
{
	if ((m_LOG.nLogDevs & LOG_DEV_WITHDATE) && tNow - m_LOG.tDate >= ONEDAY)
	{
		SetLogFile(m_LOG.szLogName);
	}
}

void CSingleLog::InitLog(log_templete* pLog)
{
	memset(pLog, 0, sizeof(log_templete));
}

// 로그 메세지 기본을 만드는 함수
void CSingleLog::SetLogBase( char* szLogBase)
{
	if (szLogBase == NULL || strlen(szLogBase) == 0)
	{
		__log_base__[0] = 0;
		return;
	}

	strncpy(__log_base__, szLogBase, strlen(szLogBase));
	if (__log_base__[strlen(__log_base__) - 1] != '/')
	{
		strcat(__log_base__, "/");
	}
}

void CSingleLog::SetLogDev( int nLogDevs)
{
	m_LOG.nLogDevs = nLogDevs;
}

void CSingleLog::SetLogLevel( int nLevel)
{
	m_LOG.nLogLevel = nLevel;
}


void CSingleLog::SetLogFile( const char* szLogFile)
{
	char			szCurTime[PATH_MAX];
	char			szFileName[PATH_MAX];
	char*			szDir;

	if (m_LOG.fpLog)
	{
		fclose(m_LOG.fpLog);
		m_LOG.fpLog = NULL;
	}

//	if (!szLogFile)
//		return;

	memset ( szFileName, INULL, sizeof ( szFileName ));

	snprintf ( szFileName, PATH_MAX, "%s%s", __log_base__, szLogFile);
	szDir = strdup(szFileName);

	MakeDirs(dirname(szDir));
	free(szDir);

	if (m_LOG.nLogDevs & LOG_DEV_WITHDATE)
	{
		time_t		tNow;
		struct tm	rt ;

		time(&tNow);
		strftime(szFileName + strlen(szFileName),
				 sizeof(szFileName) - strlen(szFileName),
				 ".%Y%m%d",
				 localtime_r(&tNow, &rt));

		m_LOG.tDate = tNow - ((tNow - g_nLocalDiff) % ONEDAY);
	}

	if (m_LOG.nLogDevs & LOG_DEV_FILE_NEW)
		m_LOG.fpLog = fopen(szFileName, "wt");
	else if (m_LOG.nLogDevs & LOG_DEV_FILE_APPEND)
		m_LOG.fpLog = fopen(szFileName, "at+");

	if (!m_LOG.fpLog)
		return;

	setlinebuf(m_LOG.fpLog);

	strncpy(m_LOG.szLogName, szLogFile, strlen(szLogFile));

	getcurtimestr(szCurTime, sizeof(szCurTime));

	fprintf(m_LOG.fpLog, "\n\n");
	fprintf(m_LOG.fpLog, 
			"\n-------------------------log open at %s-------------------------\n",
			szCurTime);
	fprintf(m_LOG.fpLog, "\n\n");
}


//--[Logging Function]------------------------------------------------------------

void CSingleLog::LogMsg( int nLevel, char* pCODE, const char* szFmt, ...)
{
	time_t			tNow;
	va_list			args;
	static	char	szLogMsg[4096];

	if (nLevel > m_LOG.nLogLevel)
		return;

	time(&tNow);
	AdjustFileName( tNow );

	va_start(args, szFmt);
	
	snprintf (szLogMsg, 4096, "[%s] | ", time2str(&tNow));
	vsnprintf(szLogMsg + strlen(szLogMsg), 4096 - strlen(szLogMsg), szFmt, args);
	snprintf (szLogMsg + strlen(szLogMsg), 4096 - strlen(szLogMsg), "\n");

	if (m_LOG.fpLog && (m_LOG.nLogDevs & (LOG_DEV_FILE_APPEND | LOG_DEV_FILE_NEW)))
	{
		fputs(szLogMsg, m_LOG.fpLog);
		fflush(m_LOG.fpLog);
	}

	if (m_LOG.nLogDevs & LOG_DEV_CONSOLE)
	{
		fputs(szLogMsg, stdout);
	}

	va_end(args);
}


//--[Utiltity Function]-----------------------------------------------------------
void CSingleLog::__time2str__(time_t* ptime, char* szTime, int nBufLen)
{
	struct tm rt ;
	strftime(szTime, nBufLen, "%Y-%m-%d, %H:%M:%S", localtime_r(ptime, &rt));
}   
        
char* CSingleLog::time2str(time_t* ptime)
{           
	__time2str__(ptime, g_szTimeStr, sizeof(g_szTimeStr));
	return g_szTimeStr;
}     

int CSingleLog::MakeDirs(const char* szPath)
{
	char		*szDirc  = strdup(szPath);
	char		*szBasec = strdup(szPath);
	char		*szDir;
	char		*szBase;

	szDir = dirname(szDirc);
	szBase = basename(szBasec);
#if 0
	if (strcmp(szBase, ".") == 0 || strcmp(szBase, "..") == 0)
	{
		free(szDirc);
		free(szBasec);
		return 0;
	}

	if (strcmp(szDir, ".") != 0 && strcmp(szDir, "/") != 0)
		MakeDirs(szDir);
#endif
	mkdir(szPath, 0777);

	free(szDirc);
	free(szBasec);

	return 0;
}

char* CSingleLog::getcurtimestr(char* szBuf, int nLen)
{               
	time_t		ct;

	if (!szBuf)     
	{       
		szBuf = (char*)g_szTimeStr;
		nLen = sizeof(g_szTimeStr);
	} 

	time(&ct);
	__time2str__(&ct, szBuf, nLen);

	return szBuf;                                                                                                                        
}
