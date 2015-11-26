#ifndef		_CSINGLELOG_HPP_
#define		_CSINGLELOG_HPP_	1

#include 	<limits.h>
#include	<sys/time.h>
#include 	<libgen.h>
#include 	<sys/stat.h>

#include 	<stdio.h>
#include 	<stdlib.h>
#include 	<string.h>
#include 	<stdarg.h>
#include 	<unistd.h>
#include 	<time.h>
#include 	<stdint.h>

#define		ONEDAY		(24 * 60 * 60)

#define    	LOG_DEV_WITHDATE        0x0001
#define 	LOG_DEV_CONSOLE         0x0002
#define 	LOG_DEV_FILE_APPEND     0x0004
#define 	LOG_DEV_FILE_NEW        0x0008

#ifndef     INULL
#define     INULL           '\0'
#endif

typedef	struct SINGLEINFO {
	FILE*		fpLog;
	int			nLogLevel;
	int			nLogDevs;
	char		szLogName[PATH_MAX];
	time_t		tDate;
} log_templete;

class CSingleLog
{
	private:
	// 싱글톤 객체 선언
	static	CSingleLog	*the_config;

	//~CSingleLog();

	char		__log_base__[256];
	int			g_nLocalDiff;
	int			m_nLevel;

	log_templete	m_LOG;

	char		g_szTimeStr[PATH_MAX];

	unsigned long long	m_lID;

	void 		 CalcDiffEpochFromLocal	() ;

	char		*GetLogPath			( void );
	char		*GetLogBase			( void );
	FILE		*GetLogFile			( void );
	int			 GetLogLevel		( void );

	log_templete	*GetLogPtr		( void );

	void			 AdjustFileName	(time_t tNow);

	void			 InitLog		(log_templete* pLog);
	void			 CloseLog		(log_templete* pLog);

	void			 SetLogFile		(const char* szLogFile);
	void			 SetLogDev		(int nLogDevs);
	void			 SetLogLevel	(int nLevel);

	void			 SetLogBase		(char* szLogBase);
	char			*time2str		(time_t* pT);
	int				 MakeDirs		(const char* szPath);
	void			 HexDump		(unsigned char* pData, int nSize, FILE* fpWrite);
	char			*getcurtimestr	(char* szBuf, int nLen);
	void			 __time2str__	(time_t* ptime, char* szTime, int nBufLen);

	void			 StartFile 		(char* pBASE, char* pPROC, unsigned long long uID);

	public:
	// 싱글톤 패턴 - 메모리에 하나 정의-구현을 위한 함수 선언
	static	CSingleLog	*instance();
	CSingleLog ();

	bool			 Initialize		(char*, unsigned long long, char* );

	void			 LogMsg			( int nLevel, char* pCODE, const char* szFmt, ...);
	void			 LogMsg			( int nLevel, int nCode, const char* szFmt, va_list* args );
	void			 LogMsgM		( int nLevel, int nCode, const char*szFmt, ...);
	void			 LogMsgM		( int nLevel, int nCode, const char*szFmt, va_list* args );
	void			 LogHexMsg		( int nLevel, const char* pBuf, int nLen);

};
#endif
