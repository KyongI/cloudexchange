/*
 * Copyright (c) 2012-2015 NEC Corporation
 * All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this
 * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html
 */

/*
 * UNC build configuration.
 */

#ifndef	_UNC_CONFIG_H
#define	_UNC_CONFIG_H

/* Product name. */
#define	UNC_PRODUCT_NAME	"Virtual Tenant Network"

/* UNC major version */
#define	UNC_VERSION_MAJOR	6

/* UNC minor version */
#define	UNC_VERSION_MINOR	1

/* UNC software revision */
#define	UNC_VERSION_REVISION	0

/* UNC software patch level. */
#define	UNC_VERSION_PATCHLEVEL	0

/* UNC software version string. */
#define	UNC_VERSION_STRING	"6.1.0.0"

/* Version suffix which represents build type. */
#define	UNC_BUILD_TYPE_SUFFIX	"-debug"

/* Installation directory for user executables. */
#define	UNC_BINDIR	"/usr/local/vtn/bin"

/* Installation directory for read-only data. */
#define	UNC_DATADIR	"/usr/local/vtn/share"

/* Installation directory for documents. */
#define	UNC_DOCDIR	"/usr/local/vtn/share/doc"

/* Installation directory for C/C++ header files. */
#define	UNC_INCLUDEDIR	"/usr/local/vtn/include"

/* Installation directory for Java programs. */
#define	UNC_JAVADIR	"/usr/local/vtn/lib/java"

/* Installation directory for library files. */
#define	UNC_LIBDIR	"/usr/local/vtn/lib"

/* Installation directory for program executables. */
#define	UNC_LIBEXECDIR	"/usr/local/vtn/libexec"

/* Installation directory for modifiable system data. */
#define	UNC_LOCALSTATEDIR	"/usr/local/vtn/var"

/* Installation directory for public configuration files for UNC modules. */
#define	UNC_MODCONFDIR	"/usr/local/vtn/modconf"

/* Installation directory for UNC modules. */
#define	UNC_MODULEDIR	"/usr/local/vtn/modules"

/* Installation directory for system admin executables. */
#define	UNC_SBINDIR	"/usr/local/vtn/sbin"

/* Installation directory for SQL scripts. */
#define	UNC_SQLDIR	"/usr/local/vtn/share/sql"

/* Installation directory for read-only system configuration. */
#define	UNC_SYSCONFDIR	"/usr/local/vtn/etc"

/* Installation directory for system admin shell scripts. */
#define	UNC_SYSSCRIPTDIR	"/usr/local/vtn/sbin"

/* Installation directory for modifiable UNC system data. */
#define	UNC_UNCWORKDIR	"/usr/local/vtn/var"

#endif	/* _UNC_CONFIG_H */
