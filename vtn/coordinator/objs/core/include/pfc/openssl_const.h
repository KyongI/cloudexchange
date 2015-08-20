/*
 * Copyright (c) 2012-2015 NEC Corporation
 * All rights reserved.
 * 
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this
 * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html
 */

/*
 * Constants defined by OpenSSL.
 */

#ifndef	_PFC_OPENSSL_CONST_H
#define	_PFC_OPENSSL_CONST_H

#define	BIO_CLOSE		0x1
#define	BIO_CTRL_EOF		0x2
#define	BIO_CTRL_FLUSH		0xb
#define	BIO_CTRL_SET_CLOSE		0x9
#define	BIO_C_GET_BUF_MEM_PTR		0x73
#define	BIO_C_SET_BUF_MEM_EOF_RETURN		0x82
#define	BIO_FLAGS_SHOULD_RETRY		0x8
#define	BIO_NOCLOSE		0x0
#define	CRYPTO_LOCK		0x1
#define	CRYPTO_UNLOCK		0x2
#define	EVP_MAX_IV_LENGTH		0x10
#define	EVP_MAX_KEY_LENGTH		0x40
#define	SSLEAY_VERSION		0x0

#endif	/* !_PFC_OPENSSL_CONST_H */
