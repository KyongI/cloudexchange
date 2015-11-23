#ifndef __GLOBAL__
#define __GLOBAL__
#pragma GCC diagnostic ignored "-Wunused-but-set-variable" 
#pragma GCC diagnostic ignored "-Wunused-variable" 
// Hides warning: 'packed' attribute ignored for field of type 'UINT8' [-Wattributes]

//-----------------------------------------------------------------------------
//// Definitions for Return
////-----------------------------------------------------------------------------
const int ITF_OK				= 0;
const int ITF_ERROR				= -1;
const int ITF_RETRY				= 1;
const int ITF_TIMEOUT			= -2;

const int ITF_TRUE				= 1;
const int ITF_FALSE				= 0;

//-----------------------------------------------------------------------------
//// Definitions for Process Exit
////-----------------------------------------------------------------------------
const int ITF_EXIT_NORMAL		=   0; 
const int ITF_EXIT_ABNORMAL		=  99; 
const int ITF_EXIT_CONFIG		=   1; // Configuration Error

typedef struct __mem_info
{
	int     seq;
	char    format_name[40+1];
	int     max_length;
	char    option_mo[1+1];
	char    data_type[1+1];
	char    default_value[7+1];
}NUD_FORMAT;

#define RESET			"\033[0m" 
#define BLACK			"\033[30m"          /* Black */ 
#define RED				"\033[31m"          /* Red */ 
#define GREEN			"\033[32m"          /* Green */ 
#define YELLOW			"\033[33m"          /* Yellow */ 
#define BLUE			"\033[34m"          /* Blue */ 
#define MAGENTA			"\033[35m"          /* Magenta */ 
#define CYAN			"\033[36m"          /* Cyan */ 
#define WHITE			"\033[37m"          /* White */ 
#define BOLDBLACK		"\033[1m\033[30m"   /* Bold Black */ 
#define BOLDRED			"\033[1m\033[31m"   /* Bold Red */ 
#define BOLDGREEN		"\033[1m\033[32m"   /* Bold Green */ 
#define BOLDYELLOW		"\033[1m\033[33m"   /* Bold Yellow */ 
#define BOLDBLUE		"\033[1m\033[34m"   /* Bold Blue */ 
#define BOLDMAGENTA		"\033[1m\033[35m"   /* Bold Magenta */ 
#define BOLDCYAN		"\033[1m\033[36m"   /* Bold Cyan */ 
#define BOLDWHITE		"\033[1m\033[37m"   /* Bold White */

#endif

// MEMBER_INFO
