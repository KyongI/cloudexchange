##
## Auto-generated build configuration.
##

ifndef	CONFIG_MK_INCLUDED

CONFIG_MK_INCLUDED	:= 1

# PFC version.
PFC_VERSION		:= 6.1.0.0
PFC_VERSION_MAJOR	:= 6
PFC_VERSION_MINOR	:= 1
PFC_VERSION_REVISION	:= 0
PFC_VERSION_PATCHLEVEL	:= 0
PFC_VERSION_STRING	:= 6.1.0.0

ARCH		:= x86
BLDDIR		:= /usr/local/vtn/vtn/coordinator/core/build
BOOST_INCDIR		:= 
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
CPPFLAGS_ALL		:= 
CXX		:= /usr/bin/g++
CXX_DEBUG		:= -g
CXX_MODE		:= -m64
CXX_NO_ALIAS		:= -fno-strict-aliasing
CXX_OPT		:= -O3
CXX_WARN		:= -Wall -Wextra -Wno-clobbered -Wno-unused-parameter -Wno-unused-local-typedefs -Wno-unused-result -Wno-format-security -Werror
DEBUG_BUILD		:= 1
DEFAULT_LIBPATH		:= /lib64 /usr/lib64 /lib /usr/lib
IPC_TMPL_SRCDIR		:= /usr/local/vtn/vtn/coordinator/ipc
JAVA_CONFIG_MK		:= /usr/local/vtn/vtn/coordinator/objs/core/java_config.mk
LINK_JNILIBDIR		:= /usr/local/vtn/vtn/coordinator/objs/ldlibs/jni
LINK_LIBDIR		:= /usr/local/vtn/vtn/coordinator/objs/ldlibs
LINUX_DIST		:= fc20
MODULE_CONFIG_MK		:= /usr/local/vtn/vtn/coordinator/objs/module-config.mk
MULTIARCH		:= 
OBJROOT		:= /usr/local/vtn/vtn/coordinator/objs/core
ODBC_DEFS_MK		:= /usr/local/vtn/vtn/coordinator/objs/odbc-defs.mk
ODBC_RULES_MK		:= /usr/local/vtn/vtn/coordinator/build/odbc-rules.mk
OPENSSL_INCDIR		:= 
OPENSSL_LIBDIR		:= 
OPENSSL_PREFIX		:= /usr
OPENSSL_RUNPATH		= $(OPENSSL_LIBDIR)
OSTYPE		:= linux
PATH_MAKE		:= /usr/bin/make
PATH_SCRIPT		:= /bin:/usr/bin
PERL		:= /usr/bin/perl
PFC_LP64		:= 1
PFC_PRODUCT_NAME		:= Virtual Tenant Network
PREFIX		:= /usr/local/vtn
REFPTR_DEBUG_ENABLED		:= 1
SHELL_PATH		:= /bin/sh
SRCROOT		:= /usr/local/vtn/vtn/coordinator/core
SUBARCH		:= x86_64
SYSLOG_TYPE		:= syslog
TIDLOG_ENABLED		:= 1
TOOLBIN		:= /usr/local/vtn/vtn/coordinator/core/tools/bin
TOOLS_DIR		:= /usr/local/vtn/vtn/coordinator/core/tools
UNC_CORE		:= 1
UNC_CORE_INCLUDE		:= /usr/local/vtn/vtn/coordinator/objs/core_include
UNC_INCDIRS		:= /usr/local/vtn/vtn/coordinator/objs/include /usr/local/vtn/vtn/coordinator/include
UNC_OBJROOT		:= /usr/local/vtn/vtn/coordinator/objs
UNC_SRCROOT		:= /usr/local/vtn/vtn/coordinator

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
INST_SYSCONFDIR		:= /usr/local/vtn/etc
INST_SYSSCRIPTDIR		:= /usr/local/vtn/sbin

AR		:= /usr/bin/ar
CAT		:= /usr/bin/cat
CP		:= /usr/bin/cp
DIFF		:= /usr/bin/diff
GTEST_CONFIG		:= /usr/bin/gtest-config
INSTALL		:= /usr/bin/install
LN		:= /usr/bin/ln
MKDIR		:= /usr/bin/mkdir
MV		:= /usr/bin/mv
SED		:= /usr/bin/sed
TAR		:= /usr/bin/tar
TOUCH		:= /usr/bin/touch

include /usr/local/vtn/vtn/coordinator/core/build/defs.mk

endif	# !CONFIG_MK_INCLUDED
