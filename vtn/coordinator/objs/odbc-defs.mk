##
## ODBC build configuration.
##

ifndef	UNC_ODBC_DEFS_MK_INCLUDED

UNC_ODBC_DEFS_MK_INCLUDED	:= 1

ODBC_CPPFLAGS		:= 
ODBC_LDFLAGS		:= -lodbc
ODBC_WRAPPER_H		:= /usr/local/vtn/vtn/coordinator/include/unc/odbc.h

endif	# !UNC_ODBC_DEFS_MK_INCLUDED
