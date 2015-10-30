#ifndef __GLOBAL__
#define __GLOBAL__
#pragma GCC diagnostic ignored "-Wunused-but-set-variable" 
#pragma GCC diagnostic ignored "-Wunused-variable" 
// Hides warning: 'packed' attribute ignored for field of type 'UINT8' [-Wattributes]

//-----------------------------------------------------------------------------
//// Definitions for Return
////-----------------------------------------------------------------------------
const int ITF_OK                = 0;
const int ITF_ERROR             = -1;
const int ITF_RETRY				= 1;
const int ITF_TIMEOUT			= -2;

const int ITF_TRUE              = 1;
const int ITF_FALSE             = 0;

//-----------------------------------------------------------------------------
//// Definitions for Process Exit
////-----------------------------------------------------------------------------
const int ITF_EXIT_NORMAL       =   0; 
const int ITF_EXIT_ABNORMAL     =  99; 
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

#endif

// MEMBER_INFO
