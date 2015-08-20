/*
 * Copyright (c) 2012-2015 NEC Corporation
 * All rights reserved.
 * 
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this
 * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html
 */

/*
 * PFC build configuration.
 */

#ifndef	_PFC_CONFIG_H
#define	_PFC_CONFIG_H

/* Product name. */
#define	PFC_PRODUCT_NAME	"Virtual Tenant Network"

/* PFC major version. */
#define	PFC_VERSION_MAJOR	6

/* PFC minor version. */
#define	PFC_VERSION_MINOR	1

/* PFC software revision. */
#define	PFC_VERSION_REVISION	0

/* PFC software patch level. */
#define	PFC_VERSION_PATCHLEVEL	0

/* PFC software version string. */
#define	PFC_VERSION_STRING	"6.1.0.0"

/* Version suffix which represents build type. */
#ifdef	PFC_VERBOSE_DEBUG
#define	PFC_DEBUG_BUILD_TYPE_SUFFIX	"-debug"
#else	/* !PFC_VERBOSE_DEBUG */
#define	PFC_DEBUG_BUILD_TYPE_SUFFIX	""
#endif	/* PFC_VERBOSE_DEBUG */

#define	PFC_BUILD_TYPE_SUFFIX	PFC_DEBUG_BUILD_TYPE_SUFFIX

/* PFC installation root. */
#define	PFC_ROOTDIR	"/usr/local/vtn"

/* Installation directory for user executables. */
#define	PFC_BINDIR	"/usr/local/vtn/bin"

/* Installation directory for Certification Authorities. */
#define	PFC_CERTSDIR	"/usr/local/vtn/etc/certs"

/* Installation directory for read-only data. */
#define	PFC_DATADIR	"/usr/local/vtn/share"

/* Installation directory for documents. */
#define	PFC_DOCDIR	"/usr/local/vtn/share/doc"

/* Installation directory for C/C++ header files. */
#define	PFC_INCLUDEDIR	"/usr/local/vtn/include"

/* Installation directory for IPC framework workspace. */
#define	PFC_IPCWORKDIR	"/usr/local/vtn/var/run/ipc"

/* Installation directory for Java programs. */
#define	PFC_JAVADIR	"/usr/local/vtn/lib/java"

/* Installation directory for library files. */
#define	PFC_LIBDIR	"/usr/local/vtn/lib"

/* Installation directory for program executables. */
#define	PFC_LIBEXECDIR	"/usr/local/vtn/libexec"

/* Installation directory for modifiable system data. */
#define	PFC_LOCALSTATEDIR	"/usr/local/vtn/var"

/* Installation directory for public configuration files for PFC modules. */
#define	PFC_MODCONFDIR	"/usr/local/vtn/modconf"

/* Installation directory for PFC modules. */
#define	PFC_MODULEDIR	"/usr/local/vtn/modules"

/* Installation directory for system admin executables. */
#define	PFC_SBINDIR	"/usr/local/vtn/sbin"

/* Installation directory for read-only system configuration. */
#define	PFC_SYSCONFDIR	"/usr/local/vtn/etc"

/* Installation directory for system admin shell scripts. */
#define	PFC_SYSSCRIPTDIR	"/usr/local/vtn/sbin"

/* Define 1 if MSG_NOSIGNAL is supported. */
#define	PFC_HAVE_MSG_NOSIGNAL	1

/* Define 1 if both SOCK_CLOEXEC and SOCK_NONBLOCK are supported. */
#define	PFC_HAVE_SOCK_CLOEXEC_NONBLOCK	1

/* Define 1 if accept4(2) is supported. */
#if	defined(_GNU_SOURCE)
#define	PFC_HAVE_ACCEPT4	1
#endif	/* _GNU_SOURCE */
#define	__PFC_HAVE_ACCEPT4	1

/* Define 1 if MSG_CMSG_CLOEXEC is supported. */
#define	PFC_HAVE_CMSG_CLOEXEC	1

/* Define 1 if O_CLOEXEC is supported. */
#define	PFC_HAVE_O_CLOEXEC	1

/* Define 1 if F_DUPFD_CLOEXEC is supported. */
#define	PFC_HAVE_F_DUPFD_CLOEXEC	1

/* Define 1 if dup3(2) is supported. */
#if	defined(_GNU_SOURCE)
#define	PFC_HAVE_DUP3	1
#endif	/* _GNU_SOURCE */
#define	__PFC_HAVE_DUP3	1

/* Define 1 if pipe2(2) is supported. */
#if	defined(_GNU_SOURCE)
#define	PFC_HAVE_PIPE2	1
#endif	/* _GNU_SOURCE */
#define	__PFC_HAVE_PIPE2	1

/* Define 1 if ATFILE syscalls, such as openat(), are supported. */
#if	defined(_ATFILE_SOURCE)
#define	PFC_HAVE_ATFILE_SYSCALL	1
#endif	/* _ATFILE_SOURCE */
#define	__PFC_HAVE_ATFILE_SYSCALL	1

/* Define 1 if fopen() recognizes "e" in mode string. */
#define	PFC_FOPEN_SUPPORTS_E	1

/* Required alignment for 64-bit integer. */
#define	PFC_ALIGNOF_INT64	8

/* Define 1 if unaligned access is allowed. */
#define	PFC_UNALIGNED_ACCESS	1

/* Define 1 if POLLRDHUP is supported. */
#define	PFC_HAVE_POLLRDHUP	1

/* Define 1 if epoll(7) is supported. */
#define	PFC_HAVE_EPOLL	1

/* Define 1 if EPOLLRDHUP is supported. */
#define	PFC_HAVE_EPOLLRDHUP	1

/* Define 1 if EPOLL_CLOEXEC is supported. */
#define	PFC_HAVE_EPOLL_CLOEXEC	1

/* Define 1 if EPOLLONESHOT is supported. */
#define	PFC_HAVE_EPOLLONESHOT	1

/* Define 1 if getresuid() is supported. */
#if	defined(_GNU_SOURCE)
#define	PFC_HAVE_GETRESUID	1
#endif	/* _GNU_SOURCE */
#define	__PFC_HAVE_GETRESUID	1

/* Define 1 if getresgid() is supported. */
#if	defined(_GNU_SOURCE)
#define	PFC_HAVE_GETRESGID	1
#endif	/* _GNU_SOURCE */
#define	__PFC_HAVE_GETRESGID	1

/* Define 1 if setresuid() is supported. */
#if	defined(_GNU_SOURCE)
#define	PFC_HAVE_SETRESUID	1
#endif	/* _GNU_SOURCE */
#define	__PFC_HAVE_SETRESUID	1

/* Define 1 if setresgid() is supported. */
#if	defined(_GNU_SOURCE)
#define	PFC_HAVE_SETRESGID	1
#endif	/* _GNU_SOURCE */
#define	__PFC_HAVE_SETRESGID	1

/* Define 1 if prctl(PR_SET_DUMPABLE) is supported. */
#define	PFC_HAVE_PRCTL_DUMPABLE	1

/* Enable or disable refptr debugging. */
#define	PFC_REFPTR_DEBUG_ENABLED	1

/* Enable or disable thread ID logging in the PFC log. */
#define	PFC_TIDLOG_ENABLED	1

#endif	/* _PFC_CONFIG_H */
