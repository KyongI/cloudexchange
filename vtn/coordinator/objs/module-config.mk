##
## Configurations to be exported to module build environment.
##

ifndef	UNC_MODULE_CONFIG_MK_INCLUDED

UNC_MODULE_CONFIG_MK_INCLUDED	:= 1

JSON_C_CPPFLAGS		:= -I/usr/include/json-c
JSON_C_LDFLAGS		:= -ljson-c
LIBCURL_LDFLAGS		:= -lcurl

endif	# !UNC_MODULE_CONFIG_MK_INCLUDED
