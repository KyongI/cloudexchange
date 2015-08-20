##
## Auto-generated build configuration.
##

ifndef	UNC_CONFIG_MK_INCLUDED

UNC_CONFIG_MK_INCLUDED	:= 1

# Software version.
UNC_VERSION_MAJOR	:= 6
UNC_VERSION_MINOR	:= 1
UNC_VERSION_REVISION	:= 0
UNC_VERSION_PATCHLEVEL	:= 0
UNC_VERSION_SUFFIX	:= 
UNC_VERSION	:= 6.1.0.0

AR		:= /usr/bin/ar
ARCH		:= x86
BLDDIR		:= /usr/local/vtn/vtn/coordinator/build
BOOST_INCDIR		:= 
CAT		:= /usr/bin/cat
CC		:= /usr/bin/gcc
CC_DEBUG		:= -g
CC_FEATURE_DEFS		:= -D_GNU_SOURCE
CC_MODE		:= -m64
CC_NO_ALIAS		:= -fno-strict-aliasing
CC_OPT		:= -O3
CC_WARN		:= -Wall -Wextra -Wno-clobbered -Wno-unused-parameter -Wno-unused-local-typedefs -Wno-unused-result -Wno-format-security -Werror
CFDEF_MODE		:= -L
CONFIG_ARCH		:= x86_64
CONFIG_OS		:= linux
CORE_EXP_INCDIR		:= /usr/local/vtn/vtn/coordinator/objs/core_include
CORE_OBJROOT		:= /usr/local/vtn/vtn/coordinator/objs/core
CORE_SRCROOT		:= /usr/local/vtn/vtn/coordinator/core
CP		:= /usr/bin/cp
CPPFLAGS_ALL		:= 
CXX		:= /usr/bin/g++
CXX_DEBUG		:= -g
CXX_MODE		:= -m64
CXX_NO_ALIAS		:= -fno-strict-aliasing
CXX_OPT		:= -O3
CXX_WARN		:= -Wall -Wextra -Wno-clobbered -Wno-unused-parameter -Wno-unused-local-typedefs -Wno-unused-result -Wno-format-security -Werror
DEBUG_BUILD		:= 1
DEFAULT_LIBPATH		:= /lib64 /usr/lib64 /lib /usr/lib
DIFF		:= /usr/bin/diff
GTEST_CONFIG		:= /usr/bin/gtest-config
INSTALL		:= /usr/bin/install
INST_BINDIR		:= /usr/local/vtn/bin
INST_CERTSDIR		:= /usr/local/vtn/etc/certs
INST_DATADIR		:= /usr/local/vtn/share
INST_DOCDIR		:= /usr/local/vtn/share/doc
INST_INCLUDEDIR		:= /usr/local/vtn/include
INST_IPCWORKDIR		:= /usr/local/vtn/var/run/ipc
INST_JAVADIR		:= /usr/local/vtn/lib/java
INST_LIBDIR		:= /usr/local/vtn/lib
INST_LIBEXECDIR		:= /usr/local/vtn/libexec
INST_LOCALSTATEDIR		:= /usr/local/vtn/var
INST_MODCONFDIR		:= /usr/local/vtn/modconf
INST_MODULEDIR		:= /usr/local/vtn/modules
INST_SBINDIR		:= /usr/local/vtn/sbin
INST_SQLDIR		:= /usr/local/vtn/share/sql
INST_SYSCONFDIR		:= /usr/local/vtn/etc
INST_SYSSCRIPTDIR		:= /usr/local/vtn/sbin
INST_UNCWORKDIR		:= /usr/local/vtn/var
IPC_TMPL_SRCDIR		:= /usr/local/vtn/vtn/coordinator/ipc
JAVA_CONFIG_MK		:= /usr/local/vtn/vtn/coordinator/objs/core/java_config.mk
LINK_JNILIBDIR		:= /usr/local/vtn/vtn/coordinator/objs/ldlibs/jni
LINK_LIBDIR		:= /usr/local/vtn/vtn/coordinator/objs/ldlibs
LINUX_DIST		:= fc20
LN		:= /usr/bin/ln
MKDIR		:= /usr/bin/mkdir
MODULE_CONFIG_MK		:= /usr/local/vtn/vtn/coordinator/objs/module-config.mk
MULTIARCH		:= 
MV		:= /usr/bin/mv
OBJROOT		:= /usr/local/vtn/vtn/coordinator/objs
ODBC_DEFS_MK		:= /usr/local/vtn/vtn/coordinator/objs/odbc-defs.mk
ODBC_RULES_MK		:= /usr/local/vtn/vtn/coordinator/build/odbc-rules.mk
OPENSSL_INCDIR		:= 
OPENSSL_LIBDIR		:= 
OPENSSL_PREFIX		:= /usr
OSTYPE		:= linux
PATH_MAKE		:= /usr/bin/make
PATH_SCRIPT		:= /bin:/usr/bin
PERL		:= /usr/bin/perl
PREFIX		:= /usr/local/vtn
REFPTR_DEBUG_ENABLED		:= 1
SED		:= /usr/bin/sed
SHELL_PATH		:= /bin/sh
SRCROOT		:= /usr/local/vtn/vtn/coordinator
SUBARCH		:= x86_64
SYSLOG_TYPE		:= syslog
TAR		:= /usr/bin/tar
TIDLOG_ENABLED		:= 1
TOOLBIN		:= /usr/local/vtn/vtn/coordinator/core/tools/bin
TOOLS_DIR		:= /usr/local/vtn/vtn/coordinator/core/tools
TOUCH		:= /usr/bin/touch
UNC_INCDIRS		:= /usr/local/vtn/vtn/coordinator/objs/include /usr/local/vtn/vtn/coordinator/include
UNC_LP64		:= 1
UNC_OBJROOT		:= /usr/local/vtn/vtn/coordinator/objs
UNC_SRCROOT		:= /usr/local/vtn/vtn/coordinator

include $(ODBC_DEFS_MK)
include $(MODULE_CONFIG_MK)
include /usr/local/vtn/vtn/coordinator/build/defs.mk

endif	# !UNC_CONFIG_MK_INCLUDED
