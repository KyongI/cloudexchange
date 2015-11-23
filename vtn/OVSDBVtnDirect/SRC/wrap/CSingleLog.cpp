#include "CSingleLog.hpp"

CSingleLog*	CSingleLog::the_config = 0;

CSingleLog::CSingleLog()
{

}

CSingleLog* CSingleLog::instance()
{
	// 객체가 null 이면 새로운 객체를 생성하고 그렇지 않으면 기존 객체를 반환
	if( !the_config )
	{
		the_config = new CSingleLog();
	}

	return (the_config);
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



char* CSingleLog::GetLogPath ( void )
{
	return ( m_LOG.szLogName );
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

void CSingleLog::CloseLog(log_templete* pLog)
{
	if (pLog->fpLog)
	{
		fclose(pLog->fpLog);
		pLog->fpLog = NULL;
	}
}

// 로그 메세지 기본을 만드는 함수
void CSingleLog::SetLogBase( char* szLogBase)
{
    if (szLogBase == NULL || strlen(szLogBase) == 0)
    {
        __log_base__[0] = 0;
        return;
    }

    strcpy(__log_base__, szLogBase);
    if (__log_base__[strlen(__log_base__) - 1] != '/')
    {
        strcat(__log_base__, "/");
    }
}

//--[Getter, Setter]-----------------------------------------------
char *CSingleLog::GetLogBase()
{
	return __log_base__;
}

FILE* CSingleLog::GetLogFile ( void )
{
	return ( m_LOG.fpLog );
}

int CSingleLog::GetLogLevel( void )
{
	return ( m_LOG.nLogLevel );
}

void CSingleLog::SetLogDev( int nLogDevs)
{
	m_LOG.nLogDevs = nLogDevs;
}

void CSingleLog::SetLogLevel( int nLevel)
{
	m_LOG.nLogLevel = nLevel;
}

log_templete* CSingleLog::GetLogPtr ( void )
{
	return ( &m_LOG );
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

	if (!szLogFile)
		return;

	memset ( szFileName, INULL, sizeof ( szFileName ));
  
  	sprintf ( szFileName, "%s%s", __log_base__, szLogFile);
	szDir = strdup(szFileName);

	MakeDirs(dirname(szDir));
	free(szDir);

	if (m_LOG.nLogDevs & LOG_DEV_WITHDATE)
	{
		time_t		tNow;
		struct tm	rt ;

		time(&tNow);
		strftime(szFileName + strlen(szFileName)
				, sizeof(szFileName) - strlen(szFileName)
				, ".%Y%m%d"
				, localtime_r(&tNow, &rt));

		m_LOG.tDate = tNow - ((tNow - g_nLocalDiff) % ONEDAY);
	}


	if (m_LOG.nLogDevs & LOG_DEV_FILE_NEW)
		m_LOG.fpLog = fopen(szFileName, "wt");
	else if (m_LOG.nLogDevs & LOG_DEV_FILE_APPEND)
		m_LOG.fpLog = fopen(szFileName, "at+");

	if (!m_LOG.fpLog)
		return;

	setlinebuf(m_LOG.fpLog);

	strcpy(m_LOG.szLogName, szLogFile);

	getcurtimestr(szCurTime, sizeof(szCurTime));

	fprintf(m_LOG.fpLog, "\n\n");
	fprintf(m_LOG.fpLog, "\n-------------------------log open at %s-------------------------\n"
				, szCurTime);
	fprintf(m_LOG.fpLog, "\n\n");
}


//--[Logging Function]------------------------------------------------------------

void CSingleLog::LogMsg( int nLevel, int nCode, const char* szFmt, va_list* args )
{
	time_t			tNow;
	static	char	szLogMsg[4096];

	if (nLevel > m_LOG.nLogLevel)
		return;

	time(&tNow);
	AdjustFileName( tNow);

	sprintf(szLogMsg, "%.6d[%s] | ", nCode, time2str(&tNow));
	vsprintf(szLogMsg + strlen(szLogMsg), szFmt, *args);
	sprintf(szLogMsg + strlen(szLogMsg), "\n");

	if (m_LOG.fpLog && (m_LOG.nLogDevs & (LOG_DEV_FILE_APPEND | LOG_DEV_FILE_NEW)))
	{
		fputs(szLogMsg, m_LOG.fpLog);
		fflush(m_LOG.fpLog);
	}

	if (m_LOG.nLogDevs & LOG_DEV_CONSOLE)
		fputs(szLogMsg, stdout);
}

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
	
	sprintf (szLogMsg, "[%s] | ", time2str(&tNow));
	vsprintf(szLogMsg + strlen(szLogMsg), szFmt, args);
	sprintf (szLogMsg + strlen(szLogMsg), "\n");

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

void CSingleLog::LogMsgM( int nLevel, int nCode, const char* szFmt, va_list* args )
{
	struct  timeval tvNow;
	static	char	szLogMsg[4096];

	if (nLevel > m_LOG.nLogLevel)
		return;

	gettimeofday(&tvNow, NULL);
	AdjustFileName( tvNow.tv_sec);

	// %d -> %lu modify by jameshans
	sprintf(szLogMsg, "%.6d[%s.%06lu] | ", nCode, time2str(&(tvNow.tv_sec) ), tvNow.tv_usec);
	vsprintf(szLogMsg + strlen(szLogMsg), szFmt, *args);
	sprintf(szLogMsg + strlen(szLogMsg), "\n");

	if (m_LOG.fpLog && (m_LOG.nLogDevs & (LOG_DEV_FILE_APPEND | LOG_DEV_FILE_NEW)))
	{
		fputs(szLogMsg, m_LOG.fpLog);
		fflush(m_LOG.fpLog);
	}

	if (m_LOG.nLogDevs & LOG_DEV_CONSOLE)
		fputs(szLogMsg, stdout);
}

void CSingleLog::LogMsgM( int nLevel, int nCode, const char* szFmt, ...)
{
	struct  timeval tvNow;
	va_list			args;
	static	char	szLogMsg[4096];

	if (nLevel > m_LOG.nLogLevel)
		return;

	gettimeofday(&tvNow, NULL);
	AdjustFileName( tvNow.tv_sec);


	va_start(args, szFmt);

	// %d -> %lu modify by jameshans
	sprintf(szLogMsg, "%.6d[%s.%06lu] | ", nCode, time2str(&(tvNow.tv_sec) ), tvNow.tv_usec);
	vsprintf(szLogMsg + strlen(szLogMsg), szFmt, args);
	sprintf(szLogMsg + strlen(szLogMsg), "\n");

	if (m_LOG.fpLog && (m_LOG.nLogDevs & (LOG_DEV_FILE_APPEND | LOG_DEV_FILE_NEW)))
	{
		fputs(szLogMsg, m_LOG.fpLog);
		fflush(m_LOG.fpLog);
	}

	if (m_LOG.nLogDevs & LOG_DEV_CONSOLE)
		fputs(szLogMsg, stdout);

	va_end(args);
}

void CSingleLog::LogHexMsg( int nLevel, const char* pBuf, int nLen)
{
	time_t			tNow;

	if (nLevel > m_LOG.nLogLevel)
		return;
	
	time(&tNow);
	AdjustFileName( tNow);

	if (nLen > 20240 ) nLen = 20240;

	if (m_LOG.fpLog && (m_LOG.nLogDevs & (LOG_DEV_FILE_APPEND | LOG_DEV_FILE_NEW)))
	{
		fprintf(m_LOG.fpLog, "[%s]\n------------------------------------------------------------------\n", time2str(&tNow));
		HexDump((unsigned char*)pBuf, nLen, m_LOG.fpLog);
		fprintf(m_LOG.fpLog, "------------------------------------------------------------------\n");
#ifndef	linux
		fflush(m_LOG.fpLog);
#endif
	}

	if (m_LOG.nLogDevs & LOG_DEV_CONSOLE)
	{
		fprintf(stdout, "[%s]\n------------------------------------------------------------------\n", time2str(&tNow));
		HexDump((unsigned char*)pBuf, nLen, stdout);
		fprintf(stdout, "------------------------------------------------------------------\n");
	}
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
    char*           szDirc  = strdup(szPath);
    char*           szBasec = strdup(szPath);
    char*           szDir;
    char*           szBase;

    szDir = dirname(szDirc);
    szBase = basename(szBasec);
    
    if (strcmp(szBase, ".") == 0 || strcmp(szBase, "..") == 0)
        goto bye;

    if (strcmp(szDir, ".") != 0 && strcmp(szDir, "/") != 0)
        MakeDirs(szDir);

    mkdir(szPath, 0777);
    
        
bye:    
    free(szDirc);
    free(szBasec);
    
    return 0;
}

void CSingleLog::HexDump(unsigned char* pData, int nSize, FILE* fpWrite)
{   
    int             i, j, k;

    for (i = 0; i < nSize; i++)
    {
        fprintf(fpWrite, "%02x ", pData[i]);
        if (i % 16 == 15 || i == nSize - 1)
        {
            for (k = i % 16; k < 15; k++)
                fprintf(fpWrite, "   ");                                                                                                 

            fprintf(fpWrite, "| ");                                                                                                      
            for (j = i - (i % 16); j <= i; j++)                                                                                          
            {       
                if (pData[j] >= 32 && pData[j] <= 126)                                                                                   
                    fprintf(fpWrite, "%c", pData[j]);                                                                                    
                else                                                                                                                     
                    fprintf(fpWrite, ".");                                                                                               
            }
                                                                                                                                         
            fprintf(fpWrite, "\n");
        }                                                                                                                                
    }   
        
    fprintf(fpWrite, "\n");                                                                                                              
}

char* CSingleLog::getcurtimestr(char* szBuf, int nLen)
{               
    time_t          ct;
                
    if (!szBuf)     
    {       
        szBuf = (char*)g_szTimeStr;                                                                                                      
        nLen = sizeof(g_szTimeStr);
    }   
    
    time(&ct);
    __time2str__(&ct, szBuf, nLen);                                                                                                      

    return szBuf;                                                                                                                        
}
