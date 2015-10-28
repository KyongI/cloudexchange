#ifndef __GLOBAL__
#define __GLOBAL__

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
